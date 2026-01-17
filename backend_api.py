"""FastAPI wrapper for the Agentic RAG System."""
import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.orchestrator import AgentOrchestrator
from retrieval.retrieval import Retriever
from src.utils.confirmation import ConfirmationClassifier
from src.utils.description_enhancer import DescriptionEnhancer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
API_KEY = os.getenv('MISTRAL_API_KEY')
INDEX_PATH = "data/faiss_cache/index.faiss"
CHUNKS_PATH = "data/chunks/Annual-Report-2024-25.json"

retriever = Retriever(INDEX_PATH, CHUNKS_PATH)
orchestrator = AgentOrchestrator(API_KEY, retriever)
confirmation_classifier = ConfirmationClassifier(API_KEY)
description_enhancer = DescriptionEnhancer(API_KEY)

# Store active sessions
sessions = {}

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    query: str
    chat_id: str
    conversation_history: List[Dict]
    pending_action: Optional[Dict] = None
    pending_state: Optional[str] = None  # "awaiting_confirmation", "awaiting_modification"
    original_query: Optional[str] = None

class ChatResponse(BaseModel):
    type: str  # "INFO_QUERY", "ACTION_REQUEST", "CONFIRMATION_NEEDED", "TICKET_GENERATED", "TICKET_EXPORTED"
    content: Dict
    pending_action: Optional[Dict] = None
    pending_state: Optional[str] = None
    original_query: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message."""
    try:
        query = request.query.strip()
        chat_id = request.chat_id
        pending_action = request.pending_action
        pending_state = request.pending_state
        original_query = request.original_query
        
        # Restore conversation history
        if chat_id not in sessions:
            sessions[chat_id] = {
                "orchestrator": AgentOrchestrator(API_KEY, retriever),
                "conversation": []
            }
        
        # Update conversation history
        for msg in request.conversation_history:
            if msg not in sessions[chat_id]["conversation"]:
                sessions[chat_id]["conversation"].append(msg)
        
        orch = sessions[chat_id]["orchestrator"]
        
        # Handle pending states
        if pending_state == "awaiting_modification" and pending_action:
            # Check satisfaction
            is_satisfied = description_enhancer.check_satisfaction(query)
            if is_satisfied:
                # Export ticket
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"user_requests/ticket_{ts}.json"
                os.makedirs("user_requests", exist_ok=True)
                with open(filename, 'w') as f:
                    json.dump(pending_action['content'], f, indent=2)
                
                return ChatResponse(
                    type="TICKET_EXPORTED",
                    content={
                        "message": f"Ticket exported to {filename}. Your request has been recorded.",
                        "filename": filename
                    },
                    pending_action=None,
                    pending_state=None,
                    original_query=None
                )
            else:
                # Modify ticket using LLM
                pending_action['content'] = description_enhancer.modify_action_json(
                    pending_action['content'], query
                )
                return ChatResponse(
                    type="TICKET_UPDATED",
                    content=pending_action['content'],
                    pending_action=pending_action,
                    pending_state="awaiting_modification",
                    original_query=original_query
                )
        
        if pending_state == "awaiting_confirmation" and pending_action:
            # Check confirmation
            action_type = pending_action['content'].get('action', 'perform this action')
            context = f"{action_type.replace('_', ' ')}"
            intent = confirmation_classifier.classify_response(query, context)
            
            if intent == "AFFIRMATIVE":
                # Generate ticket with enhanced description
                enhanced_desc = description_enhancer.enhance_description(original_query, action_type)
                pending_action['content']['description'] = enhanced_desc
                
                # Normalize date fields
                date_fields = ['date', 'start_date', 'end_date']
                for field in date_fields:
                    if field in pending_action['content'] and pending_action['content'][field]:
                        pending_action['content'][field] = description_enhancer.normalize_date(
                            pending_action['content'][field]
                        )
                
                # Normalize priority field
                if 'priority' in pending_action['content']:
                    pending_action['content']['priority'] = description_enhancer.normalize_priority(
                        pending_action['content']['priority']
                    )
                
                return ChatResponse(
                    type="TICKET_GENERATED",
                    content=pending_action['content'],
                    pending_action=pending_action,
                    pending_state="awaiting_modification",
                    original_query=original_query
                )
            elif intent == "NEGATIVE":
                return ChatResponse(
                    type="INFO_QUERY",
                    content={
                        "answer": "Understood. Let me provide some guidance instead.\n\nUsual steps to fix common issues:\n1. Check your internet connection\n2. Restart the application\n3. Try alternative methods\n4. Update to the latest version\n5. Check firewall/antivirus settings"
                    },
                    pending_action=None,
                    pending_state=None,
                    original_query=None
                )
            else:
                return ChatResponse(
                    type="CLARIFICATION_NEEDED",
                    content={"message": "I didn't understand. Please respond with 'yes' to proceed or 'no' to cancel."},
                    pending_action=pending_action,
                    pending_state="awaiting_confirmation",
                    original_query=original_query
                )
        
        # New query - process through orchestrator
        original_query = query
        response = orch.process_query(query)
        
        if response['type'] == 'ACTION_REQUEST':
            action_type = response['content'].get('action', 'unknown')
            
            # If action type is unknown or error, treat as INFO_QUERY
            if action_type in ['unknown', 'error']:
                return ChatResponse(
                    type="INFO_QUERY",
                    content={"answer": "I can help you with IT tickets, HR meetings, or leave requests. Could you please clarify what you need?"},
                    pending_action=None,
                    pending_state=None,
                    original_query=None
                )
            
            # Create confirmation message
            if action_type == 'create_it_ticket':
                issue = response['content'].get('issue_type', 'an issue')
                message = f"I understand you're facing a {issue} issue. Do you want me to create an IT ticket?"
            elif action_type == 'schedule_hr_meeting':
                meeting_type = response['content'].get('meeting_type', 'a meeting')
                message = f"I understand you want to schedule {meeting_type}. Do you want me to proceed with scheduling an HR meeting?"
            elif action_type == 'request_leave':
                leave_type = response['content'].get('leave_type', 'leave')
                message = f"I understand you want to request {leave_type}. Do you want me to submit a leave request?"
            else:
                message = "I understand you want to perform an action. Do you want me to proceed?"
            
            return ChatResponse(
                type="CONFIRMATION_NEEDED",
                content={"message": message},
                pending_action=response,
                pending_state="awaiting_confirmation",
                original_query=original_query
            )
        else:
            return ChatResponse(
                type="INFO_QUERY",
                content={"answer": response['content']},
                pending_action=None,
                pending_state=None,
                original_query=None
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
