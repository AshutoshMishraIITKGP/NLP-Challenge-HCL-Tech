import os
import sys
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.langchain_router import LangChainIntentRouter
from agent.action_generator import ActionGenerator
from rag.langchain_answer import LangChainAnswerGenerator
from utils.logger import SystemLogger
from utils.conversation import ConversationHistory


class AgentOrchestrator:
    """Orchestrates the complete agent workflow: intent classification -> routing -> response generation."""
    
    # Safety keywords that trigger automatic INFO_QUERY routing
    SAFETY_KEYWORDS = [
        "confidential", "internal", "ignore rules", "leak", "secret", 
        "inside information", "private", "non-public", "bypass", "override"
    ]
    
    def __init__(self, api_key, retriever):
        """
        Initialize the orchestrator with all required components.
        
        Args:
            api_key: Mistral API key
            retriever: Retrieval system instance
        """
        self.intent_router = LangChainIntentRouter(api_key)
        self.answer_generator = LangChainAnswerGenerator(api_key, retriever)
        self.action_generator = ActionGenerator(api_key)
        self.logger = SystemLogger()
        self.conversation = ConversationHistory()
    
    def process_query(self, query):
        """
        Process user query through the complete agent pipeline.
        
        Args:
            query: User input string
            
        Returns:
            dict: Response containing type, content, and metadata
        """
        print(f"\n[ORCHESTRATOR] Processing query: {query}")
        self.logger.log_query(query)
        
        try:
            # Step 0: Safety override check
            query_lower = query.lower()
            if any(keyword in query_lower for keyword in self.SAFETY_KEYWORDS):
                print("[ORCHESTRATOR] Safety override triggered - routing to INFO_QUERY")
                safety_response = "This is a publicly released annual report. I cannot provide confidential or internal-only information. I can summarize publicly disclosed risks and challenges if you'd like."
                self.logger.log_response("SAFETY_REFUSAL", safety_response)
                self.conversation.add_exchange(query, safety_response, "INFO_QUERY")
                return {
                    "type": "INFO_QUERY",
                    "content": safety_response,
                    "query": query
                }
            
            # Step 1: Classify intent
            print("[ORCHESTRATOR] Step 1: Classifying intent...")
            intent = self.intent_router.classify_intent(query)
            print(f"[ORCHESTRATOR] Intent classified as: {intent}")
            self.logger.log_query(query, intent)
            
            # Get conversation context
            context = self.conversation.get_context(last_n=3)
            
            # Step 2: Route based on intent
            if intent == "INFO_QUERY":
                print("[ORCHESTRATOR] Step 2: Routing to RAG Answer Generator...")
                answer = self.answer_generator.generate_answer(query, context)
                print("[ORCHESTRATOR] Answer generated successfully")
                self.logger.log_response("INFO_QUERY", answer)
                self.conversation.add_exchange(query, answer, "INFO_QUERY")
                
                return {
                    "type": "INFO_QUERY",
                    "content": answer,
                    "query": query
                }
            
            elif intent == "ACTION_REQUEST":
                print("[ORCHESTRATOR] Step 2: Routing to Action Generator...")
                action_json = self.action_generator.generate_action(query)
                print("[ORCHESTRATOR] Action JSON generated successfully")
                self.logger.log_action(action_json.get('action', 'unknown'), "PENDING")
                self.conversation.add_exchange(query, action_json, "ACTION_REQUEST")
                
                return {
                    "type": "ACTION_REQUEST",
                    "content": action_json,
                    "query": query
                }
            
            else:
                # Fallback
                print("[ORCHESTRATOR] Warning: Unknown intent, defaulting to INFO_QUERY")
                answer = self.answer_generator.generate_answer(query, context)
                self.logger.log_response("INFO_QUERY", answer)
                self.conversation.add_exchange(query, answer, "INFO_QUERY")
                
                return {
                    "type": "INFO_QUERY",
                    "content": answer,
                    "query": query
                }
        
        except Exception as e:
            self.logger.log_error(e)
            raise
    
    def format_response(self, response):
        """
        Format the response for clean output.
        
        Args:
            response: Response dict from process_query
            
        Returns:
            str: Formatted response string
        """
        output = []
        output.append("=" * 80)
        output.append(f"QUERY: {response['query']}")
        output.append(f"TYPE: {response['type']}")
        output.append("=" * 80)
        
        if response['type'] == "INFO_QUERY":
            output.append(response['content'])
        
        elif response['type'] == "ACTION_REQUEST":
            output.append("\nACTION JSON:")
            output.append(json.dumps(response['content'], indent=2))
            output.append("\nNOTE: This is a mock action. No real execution performed.")
        
        output.append("=" * 80)
        
        return "\n".join(output)
