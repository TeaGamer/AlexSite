"""Test API endpoints"""
import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing /health")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def test_config():
    """Test config endpoint"""
    print("\n" + "="*60)
    print("Testing /api/config")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/config")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def test_chat():
    """Test chat endpoint"""
    print("\n" + "="*60)
    print("Testing /api/rag/chat")
    print("="*60)
    
    payload = {
        "question": "What are the graduation requirements?",
        "top_k": 5,
        "session_id": "test-session"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/rag/chat",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Answer: {result.get('answer', 'No answer')[:200]}...")
    print(f"Sources: {len(result.get('sources', []))}")
    
    assert response.status_code == 200


def test_search():
    """Test search endpoint"""
    print("\n" + "="*60)
    print("Testing /api/rag/search")
    print("="*60)
    
    payload = {
        "query": "graduation requirements",
        "top_k": 3
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/rag/search",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Results found: {result.get('total_results', 0)}")
    
    if result.get('results'):
        for i, res in enumerate(result['results'][:2], 1):
            print(f"  {i}. {res['source']} (score: {res['relevance_score']:.2f})")
    
    assert response.status_code == 200


def test_documents():
    """Test documents endpoint"""
    print("\n" + "="*60)
    print("Testing /api/rag/documents")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/rag/documents")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total documents: {result.get('total_count', 0)}")
    
    if result.get('documents'):
        print("Documents:")
        for doc in result['documents'][:3]:
            print(f"  - {doc['filename']} ({doc['chunks_count']} chunks)")
    
    assert response.status_code == 200


def test_upload_document():
    """Test document upload"""
    print("\n" + "="*60)
    print("Testing /api/rag/upload-document")
    print("="*60)
    
    # Create a test file
    test_file_path = "test_document.txt"
    test_content = """
    This is a test document for the RAG system.
    It contains information about the study program.
    Students must complete 120 credits to graduate.
    The program includes core courses and electives.
    """
    
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'source_name': 'Test Document'}
            
            response = requests.post(
                f"{BASE_URL}/api/rag/upload-document",
                files=files,
                data=data
            )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        if result.get('document'):
            doc = result['document']
            print(f"Document ID: {doc['document_id']}")
            print(f"Chunks created: {doc['chunks_count']}")
        
        assert response.status_code == 200
    
    finally:
        # Clean up
        Path(test_file_path).unlink(missing_ok=True)


def test_upload_dataset():
    """Test dataset upload"""
    print("\n" + "="*60)
    print("Testing /api/rag/upload-dataset")
    print("="*60)
    
    # Create a test CSV
    test_file_path = "test_dataset.csv"
    csv_content = """source,content
Study Program Handbook,"All students must complete the core curriculum"
Academic Calendar,"Students need 120 credits to graduate"
Course Catalog,"Spring semester includes advanced courses"
"""
    
    with open(test_file_path, 'w') as f:
        f.write(csv_content)
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'text_column': 'content',
                'source_column': 'source'
            }
            
            response = requests.post(
                f"{BASE_URL}/api/rag/upload-dataset",
                files=files,
                data=data
            )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Documents added: {len(result.get('document_ids', []))}")
        
        assert response.status_code == 200
    
    finally:
        Path(test_file_path).unlink(missing_ok=True)


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("RAG Chatbot API Tests")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    
    try:
        test_health()
        test_config()
        test_documents()
        test_search()
        test_chat()
        test_upload_document()
        test_upload_dataset()
        
        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print(f"Make sure server is running at {BASE_URL}")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    run_all_tests()
