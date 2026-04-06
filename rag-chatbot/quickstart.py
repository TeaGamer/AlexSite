"""Quick start script for RAG system"""
import argparse
import json
from pathlib import Path
from app.services.rag_service import RAGService
from app.utils.dataset_manager import DatasetManager
from app.utils.fine_tuner import create_sample_training_data


def setup_demo_data(output_dir: str = "./demo_data"):
    """Setup demo dataset"""
    Path(output_dir).mkdir(exist_ok=True)
    
    demo_data = [
        {
            "title": "Course Requirements",
            "content": """All students in our program must complete the core curriculum which includes:
            - 4 semesters of mathematics courses
            - 3 semesters of programming courses
            - 2 semesters of physics
            - General education courses totaling 15 credits
            """,
            "source": "Study Program Handbook"
        },
        {
            "title": "Graduation Requirements",
            "content": """To graduate from our program, students must:
            - Complete a minimum of 120 credit hours
            - Maintain a minimum GPA of 2.0
            - Pass all core courses with a grade of C or better
            - Complete the senior capstone project
            - Fulfill all elective requirements by their major
            """,
            "source": "Academic Calendar"
        },
        {
            "title": "First Year Courses",
            "content": """First year students typically take:
            Semester 1:
            - MATH 101: Calculus I (4 credits)
            - CS 101: Introduction to Programming (4 credits)
            - PHYS 101: Physics I (4 credits)
            - ENG 101: English Composition (3 credits)
            
            Semester 2:
            - MATH 102: Calculus II (4 credits)
            - CS 102: Data Structures (4 credits)
            - PHYS 102: Physics II (4 credits)
            - GEN 101: General Education Elective (3 credits)
            """,
            "source": "Course Catalog 2024"
        },
        {
            "title": "Internship Program",
            "content": """Our internship program is mandatory for all students:
            - 6-month internship in junior year
            - Minimum 20 hours per week commitment
            - Supervised by faculty mentor
            - Industry partner companies include leading tech firms
            - Students receive course credit and stipend
            - Internship typically leads to job offers
            """,
            "source": "Career Services"
        },
        {
            "title": "Capstone Project",
            "content": """The capstone project is the culmination of the program:
            - Completed in the final year (2 semesters)
            - Student forms team of 3-4 peers
            - Real-world problem from industry partner
            - Results in product/solution deployment
            - Presentation to faculty and industry representatives
            - Counts as 6 credit hours total
            """,
            "source": "Department Guidelines"
        }
    ]
    
    # Save as JSON and CSV
    json_path = Path(output_dir) / "study_program.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)
    
    # Save as CSV
    csv_path = Path(output_dir) / "study_program.csv"
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "content", "source"])
        writer.writeheader()
        for item in demo_data:
            writer.writerow(item)
    
    print(f"Demo data created in {output_dir}/")
    print(f"  - {json_path}")
    print(f"  - {csv_path}")
    
    return demo_data


def test_rag_system():
    """Test RAG system with demo questions"""
    print("\n" + "="*60)
    print("Testing RAG System with Demo Questions")
    print("="*60)
    
    rag_service = RAGService()
    
    # First, setup demo data
    demo_data = setup_demo_data()
    
    # Add demo data to RAG
    print("\nAdding demo data to vector store...")
    doc_ids = rag_service.add_from_dataset(
        dataset=demo_data,
        text_column="content",
        source_column="source"
    )
    print(f"Added {len(doc_ids)} documents")
    
    # Test queries
    test_queries = [
        "What are the graduation requirements?",
        "How many credits do I need?",
        "What courses are required in first year?",
        "Is internship mandatory?",
        "Tell me about the capstone project",
    ]
    
    print("\n" + "="*60)
    print("Running Test Queries")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 60)
        
        try:
            answer, sources = rag_service.query(query, top_k=3)
            print(f"Answer: {answer[:500]}...")
            print(f"\nSources ({len(sources)}):")
            for j, source in enumerate(sources, 1):
                print(f"  {j}. {source['source']} (Relevance: {source['similarity']:.2f})")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


def create_training_data_sample():
    """Create sample training data for fine-tuning"""
    print("\nCreating sample training data...")
    create_sample_training_data()
    print("Sample training data created: sample_training_data.json")


def main():
    parser = argparse.ArgumentParser(description="RAG Chatbot Quick Start")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run demo tests"
    )
    parser.add_argument(
        "--setup-data",
        action="store_true",
        help="Setup demo data only"
    )
    parser.add_argument(
        "--training-data",
        action="store_true",
        help="Create sample training data"
    )
    
    args = parser.parse_args()
    
    if args.test:
        test_rag_system()
    elif args.setup_data:
        setup_demo_data()
    elif args.training_data:
        create_training_data_sample()
    else:
        print("RAG Chatbot Quick Start")
        print("-" * 40)
        print("Usage:")
        print("  python quickstart.py --test           # Run demo tests")
        print("  python quickstart.py --setup-data     # Setup demo data")
        print("  python quickstart.py --training-data  # Create training data sample")


if __name__ == "__main__":
    main()
