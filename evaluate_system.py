"""Evaluation script for Agentic RAG System."""
import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.orchestrator import AgentOrchestrator
from retrieval.retrieval import Retriever
from src.utils.description_enhancer import DescriptionEnhancer

# Test cases for evaluation
INFO_QUERIES = [
    "What is HCLTech's revenue for FY25?",
    "Tell me about HCLTech's global presence",
    "What are the key achievements in 2024?",
    "How many employees does HCLTech have?",
    "What is the company's growth rate?"
]

ACTION_QUERIES = [
    "My VPN is not working",
    "I need to schedule a meeting with HR",
    "I want to apply for leave",
    "My laptop screen is broken",
    "Schedule a performance review meeting"
]

def evaluate_intent_classification():
    """Evaluate intent classification accuracy."""
    print("\n=== Intent Classification Evaluation ===")
    
    API_KEY = os.getenv('MISTRAL_API_KEY')
    INDEX_PATH = "data/faiss_cache/index.faiss"
    CHUNKS_PATH = "data/chunks/Annual-Report-2024-25.json"
    
    retriever = Retriever(INDEX_PATH, CHUNKS_PATH)
    orchestrator = AgentOrchestrator(API_KEY, retriever)
    
    correct = 0
    total = 0
    
    # Test INFO_QUERY classification
    for query in INFO_QUERIES:
        response = orchestrator.process_query(query)
        if response['type'] == 'INFO_QUERY':
            correct += 1
        total += 1
        print(f"✓ INFO: {query[:50]}... -> {response['type']}")
    
    # Test ACTION_REQUEST classification
    for query in ACTION_QUERIES:
        response = orchestrator.process_query(query)
        if response['type'] == 'ACTION_REQUEST':
            correct += 1
        total += 1
        print(f"✓ ACTION: {query[:50]}... -> {response['type']}")
    
    accuracy = (correct / total) * 100
    print(f"\n✅ Intent Classification Accuracy: {accuracy:.2f}%")
    return accuracy

def evaluate_retrieval_quality():
    """Evaluate retrieval relevance."""
    print("\n=== Retrieval Quality Evaluation ===")
    
    INDEX_PATH = "data/faiss_cache/index.faiss"
    CHUNKS_PATH = "data/chunks/Annual-Report-2024-25.json"
    
    retriever = Retriever(INDEX_PATH, CHUNKS_PATH)
    
    # Test queries with expected page ranges
    test_cases = [
        ("HCLTech revenue FY25", [4, 5]),
        ("company global presence", [1, 2, 3]),
        ("employee count", [4, 5]),
    ]
    
    total_score = 0
    for query, expected_pages in test_cases:
        results = retriever.retrieve(query, top_k=5)
        retrieved_pages = [r['page'] for r in results]
        
        # Check if any expected page is in top results
        hit = any(page in retrieved_pages for page in expected_pages)
        score = 1.0 if hit else 0.0
        total_score += score
        
        print(f"Query: '{query}'")
        print(f"  Retrieved pages: {retrieved_pages[:3]}")
        print(f"  Expected pages: {expected_pages}")
        print(f"  Hit: {'✓' if hit else '✗'}")
    
    avg_score = (total_score / len(test_cases)) * 100
    print(f"\n✅ Retrieval Hit Rate: {avg_score:.2f}%")
    return avg_score

def evaluate_response_time():
    """Evaluate average response time."""
    print("\n=== Response Time Evaluation ===")
    
    API_KEY = os.getenv('MISTRAL_API_KEY')
    INDEX_PATH = "data/faiss_cache/index.faiss"
    CHUNKS_PATH = "data/chunks/Annual-Report-2024-25.json"
    
    retriever = Retriever(INDEX_PATH, CHUNKS_PATH)
    orchestrator = AgentOrchestrator(API_KEY, retriever)
    
    times = []
    
    for query in INFO_QUERIES[:3]:  # Test 3 queries
        start = time.time()
        orchestrator.process_query(query)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Query: '{query[:40]}...' -> {elapsed:.2f}s")
    
    avg_time = sum(times) / len(times)
    print(f"\n✅ Average Response Time: {avg_time:.2f}s")
    return avg_time

def evaluate_action_extraction():
    """Evaluate action parameter extraction accuracy."""
    print("\n=== Action Extraction Evaluation ===")
    
    API_KEY = os.getenv('MISTRAL_API_KEY')
    INDEX_PATH = "data/faiss_cache/index.faiss"
    CHUNKS_PATH = "data/chunks/Annual-Report-2024-25.json"
    
    retriever = Retriever(INDEX_PATH, CHUNKS_PATH)
    orchestrator = AgentOrchestrator(API_KEY, retriever)
    
    test_cases = [
        ("My VPN is not working", "create_it_ticket", "vpn"),
        ("I need to schedule a meeting with HR", "schedule_hr_meeting", "general"),
        ("I want to apply for sick leave", "request_leave", "sick"),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for query, expected_action, expected_param in test_cases:
        response = orchestrator.process_query(query)
        if response['type'] == 'ACTION_REQUEST':
            action = response['content'].get('action', '')
            if action == expected_action:
                correct += 1
                print(f"✓ '{query[:40]}...' -> {action}")
            else:
                print(f"✗ '{query[:40]}...' -> {action} (expected {expected_action})")
        else:
            print(f"✗ '{query[:40]}...' -> Not classified as ACTION_REQUEST")
    
    accuracy = (correct / total) * 100
    print(f"\n✅ Action Extraction Accuracy: {accuracy:.2f}%")
    return accuracy

def evaluate_data_normalization():
    """Evaluate date and priority normalization."""
    print("\n=== Data Normalization Evaluation ===")
    
    API_KEY = os.getenv('MISTRAL_API_KEY')
    enhancer = DescriptionEnhancer(API_KEY)
    
    # Test date normalization
    date_tests = [
        ("tomorrow", r"^\d{4}-\d{2}-\d{2}$"),
        ("18th Jan", r"^\d{4}-\d{2}-\d{2}$"),
        ("2026-01-20", r"^2026-01-20$"),
    ]
    
    date_correct = 0
    for date_input, pattern in date_tests:
        normalized = enhancer.normalize_date(date_input)
        import re
        if re.match(pattern, normalized):
            date_correct += 1
            print(f"✓ Date: '{date_input}' -> '{normalized}'")
        else:
            print(f"✗ Date: '{date_input}' -> '{normalized}'")
    
    # Test priority normalization
    priority_tests = [
        ("urgent", "High"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("critical", "High"),
    ]
    
    priority_correct = 0
    for priority_input, expected in priority_tests:
        normalized = enhancer.normalize_priority(priority_input)
        if normalized == expected:
            priority_correct += 1
            print(f"✓ Priority: '{priority_input}' -> '{normalized}'")
        else:
            print(f"✗ Priority: '{priority_input}' -> '{normalized}' (expected {expected})")
    
    total_correct = date_correct + priority_correct
    total_tests = len(date_tests) + len(priority_tests)
    accuracy = (total_correct / total_tests) * 100
    
    print(f"\n✅ Normalization Accuracy: {accuracy:.2f}%")
    return accuracy

def generate_metrics_report():
    """Generate comprehensive metrics report."""
    print("\n" + "="*60)
    print("AGENTIC RAG SYSTEM - PERFORMANCE EVALUATION")
    print("="*60)
    
    metrics = {}
    
    try:
        metrics['intent_accuracy'] = evaluate_intent_classification()
    except Exception as e:
        print(f"Error in intent classification: {e}")
        metrics['intent_accuracy'] = 0
    
    try:
        metrics['retrieval_hit_rate'] = evaluate_retrieval_quality()
    except Exception as e:
        print(f"Error in retrieval evaluation: {e}")
        metrics['retrieval_hit_rate'] = 0
    
    try:
        metrics['avg_response_time'] = evaluate_response_time()
    except Exception as e:
        print(f"Error in response time evaluation: {e}")
        metrics['avg_response_time'] = 0
    
    try:
        metrics['action_accuracy'] = evaluate_action_extraction()
    except Exception as e:
        print(f"Error in action extraction: {e}")
        metrics['action_accuracy'] = 0
    
    try:
        metrics['normalization_accuracy'] = evaluate_data_normalization()
    except Exception as e:
        print(f"Error in normalization evaluation: {e}")
        metrics['normalization_accuracy'] = 0
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY METRICS")
    print("="*60)
    print(f"Intent Classification Accuracy: {metrics['intent_accuracy']:.2f}%")
    print(f"Retrieval Hit Rate: {metrics['retrieval_hit_rate']:.2f}%")
    print(f"Action Extraction Accuracy: {metrics['action_accuracy']:.2f}%")
    print(f"Data Normalization Accuracy: {metrics['normalization_accuracy']:.2f}%")
    print(f"Average Response Time: {metrics['avg_response_time']:.2f}s")
    print("="*60)
    
    # Save to file
    metrics['timestamp'] = datetime.now().isoformat()
    with open('metrics_report.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("\n✅ Metrics saved to metrics_report.json")
    
    return metrics

if __name__ == "__main__":
    generate_metrics_report()
