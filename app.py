"""
Main application entry point for the Agentic RAG System.
Handles CLI interaction and orchestrates the complete workflow.
"""
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.orchestrator import AgentOrchestrator
from retrieval.retrieval import Retriever
from src.utils.validator import InputValidator
from src.utils.confirmation import ConfirmationClassifier
from src.utils.metrics import PerformanceMonitor
from src.utils.description_enhancer import DescriptionEnhancer
from datetime import datetime


# Get API key from environment
API_KEY = os.getenv('MISTRAL_API_KEY')

if not API_KEY:
    print("ERROR: MISTRAL_API_KEY not found in .env file")
    sys.exit(1)

# Paths (adjust based on your setup)
INDEX_PATH = "data/faiss_cache/index.faiss"
CHUNKS_PATH = "data/chunks/Annual-Report-2024-25.json"


def main():
    """Main application loop."""
    
    print("=" * 80)
    print("AGENTIC RAG SYSTEM FOR IT SERVICE DESK AND HR OPERATIONS")
    print("=" * 80)
    print("\nInitializing system...")
    
    # Check if required files exist
    if not os.path.exists(INDEX_PATH):
        print(f"ERROR: FAISS index not found at {INDEX_PATH}")
        print("Please run the ingestion pipeline first to build the index.")
        return
    
    if not os.path.exists(CHUNKS_PATH):
        print(f"ERROR: Chunks file not found at {CHUNKS_PATH}")
        print("Please run the ingestion pipeline first to create chunks.")
        return
    
    # Initialize retriever
    print("Loading FAISS index and document chunks...")
    retriever = Retriever(INDEX_PATH, CHUNKS_PATH)
    print("[OK] Retriever initialized")
    
    # Initialize orchestrator
    print("Initializing agent orchestrator...")
    orchestrator = AgentOrchestrator(API_KEY, retriever)
    print("[OK] Orchestrator initialized")
    
    # Initialize confirmation classifier
    confirmation_classifier = ConfirmationClassifier(API_KEY)
    
    # Initialize performance monitor
    performance_monitor = PerformanceMonitor()
    
    # Initialize description enhancer
    description_enhancer = DescriptionEnhancer(API_KEY)
    
    print("\nSystem ready! Type 'quit' or 'exit' to stop.\n")
    print(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Main interaction loop
    pending_action = None  # Store pending action for confirmation
    pending_description_edit = False  # Track if waiting for description edit
    pending_json_modification = False  # Track if waiting for JSON modification
    original_query = None  # Store original query for description enhancement
    
    while True:
        try:
            # Get user input
            query = input("\nYour query: ").strip()
            
            # Check for exit commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            # Skip empty queries
            if not query:
                continue
            
            # Validate input
            is_valid, error_msg = InputValidator.validate(query)
            if not is_valid:
                print(f"\n[VALIDATION ERROR] {error_msg}")
                continue
            
            # Check if user is modifying JSON
            if pending_json_modification and pending_action:
                # First check if user wants to write custom description
                wants_custom = description_enhancer.wants_custom_description(query)
                
                if wants_custom:
                    print("\nYour description: ", end="")
                    custom_desc = input().strip()
                    pending_action['content']['description'] = custom_desc
                    
                    # Show updated JSON
                    print(f"\nUpdated Ticket:")
                    print(json.dumps(pending_action['content'], indent=2))
                    print("\nDo you want to modify the ticket? (If you want to write your own custom description, please inform): ", end="")
                    continue
                
                # Check satisfaction level first
                print("\n[DEBUG] Checking satisfaction...", end="", flush=True)
                is_satisfied = description_enhancer.check_satisfaction(query)
                print(f" Result: {'SATISFIED' if is_satisfied else 'UNSATISFIED'}")
                
                if is_satisfied:
                    # User is satisfied, export JSON
                    print("\nExporting .json...")
                    
                    # Create filename with timestamp
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"user_requests/ticket_{ts}.json"
                    
                    # Export JSON
                    with open(filename, 'w') as f:
                        json.dump(pending_action['content'], f, indent=2)
                    
                    print(f"[OK] Ticket exported to {filename}")
                    print("\nYour request has been recorded. Our support team will review it shortly.")
                    
                    pending_action = None
                    pending_json_modification = False
                    original_query = None
                    performance_monitor.end_query(success=True, query_type='ACTION_REQUEST')
                    continue
                else:
                    # User wants changes, modify JSON
                    pending_action['content'] = description_enhancer.modify_action_json(
                        pending_action['content'], 
                        query
                    )
                    
                    # Show updated JSON
                    print(f"\nUpdated Ticket:")
                    print(json.dumps(pending_action['content'], indent=2))
                    print("\nDo you want to modify the ticket? (If you want to write your own custom description, please inform): ", end="")
                    continue
            
            # Check if user is editing description
            if pending_description_edit and pending_action:
                # User provided custom description (paste exactly as-is)
                pending_action['content']['description'] = query
                
                # Show updated JSON and ask for more changes
                print(f"\nUpdated Ticket:")
                print(json.dumps(pending_action['content'], indent=2))
                print("\nDo you want to modify the ticket? (If you want to write your own custom description, please inform): ", end="")
                
                pending_description_edit = False
                pending_json_modification = True
                continue
            
            # Check if user is confirming a pending action
            if pending_action:
                # Use LLM to understand semantic meaning
                action_type = pending_action['content'].get('action', 'perform this action')
                context = f"{action_type.replace('_', ' ')}"
                
                intent = confirmation_classifier.classify_response(query, context)
                
                if intent == "AFFIRMATIVE":
                    # Enhance description and show full JSON
                    print("\nGenerating ticket...", end="", flush=True)
                    enhanced_desc = description_enhancer.enhance_description(original_query, action_type)
                    pending_action['content']['description'] = enhanced_desc
                    print(" Done!")
                    
                    # Show complete JSON
                    print(f"\nGenerated Ticket:")
                    print(json.dumps(pending_action['content'], indent=2))
                    print("\nDo you want to modify the ticket? (If you want to write your own custom description, please inform): ", end="")
                    pending_json_modification = True
                    continue
                elif intent == "NEGATIVE":
                    print("\nUnderstood. Let me provide some guidance instead.")
                    print("\nUsual steps to fix VPN issues:")
                    print("1. Check your internet connection")
                    print("2. Restart the VPN application")
                    print("3. Try connecting to a different VPN server")
                    print("4. Update the VPN client to the latest version")
                    print("5. Check firewall/antivirus settings")
                    print("\n(Note: FAQ-based guidance feature will be enhanced in future versions)")
                    
                    pending_action = None
                    original_query = None
                    performance_monitor.end_query(success=True, query_type='INFO_QUERY')
                    continue
                else:  # UNCLEAR
                    print("\nI didn't understand. Please respond with 'yes' to proceed or 'no' to cancel.")
                    continue
            
            # Process query through orchestrator
            performance_monitor.start_query()
            original_query = query  # Store for description enhancement
            response = orchestrator.process_query(query)
            
            # If it's an action request, ask for confirmation first
            if response['type'] == 'ACTION_REQUEST':
                pending_action = response
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Extract action details
                action_type = response['content'].get('action', 'unknown')
                
                # Create natural language summary
                if action_type == 'create_it_ticket':
                    issue = response['content'].get('issue_type', 'an issue')
                    print(f"\n[{timestamp}] I understand you're facing a {issue} issue. Do you want me to create an IT ticket?")
                elif action_type == 'schedule_hr_meeting':
                    meeting_type = response['content'].get('meeting_type', 'a meeting')
                    print(f"\n[{timestamp}] I understand you want to schedule {meeting_type}. Do you want me to proceed with scheduling an HR meeting?")
                elif action_type == 'request_leave':
                    leave_type = response['content'].get('leave_type', 'leave')
                    print(f"\n[{timestamp}] I understand you want to request {leave_type}. Do you want me to submit a leave request?")
                else:
                    print(f"\n[{timestamp}] I understand you want to perform an action. Do you want me to proceed?")
                
                performance_monitor.end_query(success=True, query_type='ACTION_REQUEST')
            else:
                # For INFO_QUERY, display immediately with timestamp
                timestamp = datetime.now().strftime('%H:%M:%S')
                formatted_output = orchestrator.format_response(response)
                print(f"\n[{timestamp}] {formatted_output}\n")
                performance_monitor.end_query(success=True, query_type='INFO_QUERY')
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        
        except Exception as e:
            print(f"\nERROR: {str(e)}")
            print("Please try again with a different query.\n")
            performance_monitor.end_query(success=False)
    
    # Save metrics on exit
    print("\n" + "="*80)
    print("SESSION SUMMARY")
    print("="*80)
    summary = performance_monitor.get_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    performance_monitor.save_metrics()
    print("\nMetrics saved to logs/metrics.json")


if __name__ == "__main__":
    main()
