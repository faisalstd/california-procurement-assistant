"""
Demo Questions for Testing the California Procurement Assistant
Run this file to test various query types
"""

from ollama_agent import OllamaAgent
import time

# Initialize agent
print("Initializing agent...")
agent = OllamaAgent()
print("Agent ready!\n")
print("="*60)

# Test questions covering all functionality
demo_questions = [
    # Basic Statistics
    "What is the total spending in 2014?",
    "How many purchases were made in 2013?",
    "What's the average purchase amount?",
    
    # Department Analysis
    "Which department spent the most money?",
    "Show me IT department purchases",
    
    # Supplier Analysis
    "Top 5 suppliers by revenue",
    "Who are the biggest suppliers?",
    
    # Item Analysis
    "Most frequently ordered items",
    "What are the top selling products?",
    
    # Time-based Analysis
    "What's the highest spending quarter?",
    "Show monthly spending trend",
    "Compare spending between 2013 and 2014",
    
    # Price Range Queries
    "Show purchases over 1 million dollars",
    "Find the 10 most expensive purchases",
    
    # Acquisition Methods
    "What acquisition methods are most popular?",
    "How many purchases use each acquisition method?",
    
    # Trend Analysis
    "Show spending trend over time",
    "What's the yearly spending analysis?",
]

def test_questions():
    """Test all demo questions"""
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            answer = agent.answer_question(question)
            elapsed = time.time() - start_time
            
            print(answer)
            print(f"\n⏱️ Response time: {elapsed:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("="*60)
        
        # Optional: pause between questions
        if i < len(demo_questions):
            input("\nPress Enter for next question...")

if __name__ == "__main__":
    print("\n🚀 CALIFORNIA PROCUREMENT ASSISTANT - DEMO\n")
    print("This will test various query types to demonstrate functionality")
    print("="*60)
    
    test_questions()
    
    print("\n✅ Demo completed!")
    print("\nThese questions demonstrate:")
    print("• Natural language understanding")
    print("• MongoDB query generation")
    print("• Data aggregation and analysis")
    print("• Various response formats")