"""
Main entry point for running the news gatherer agent
"""
from agents.news_gatherer import NewsGathererAgent
from langchain_core.messages import HumanMessage, AIMessage
import json


def print_results(state):
    """Pretty print the agent's conversation and results"""
    
    print(f"\n{'='*80}")
    print(f"📊 WORKFLOW RESULTS")
    print(f"{'='*80}")
    print(f"Status: {state['status']}")
    print(f"Tool Calls: {state['tool_calls_count']}")
    print(f"Timestamp: {state['timestamp']}")
    
    if state.get('error'):
        print(f"❌ Error: {state['error']}")
        return
    
    print(f"\n{'='*80}")
    print(f"💬 CONVERSATION")
    print(f"{'='*80}\n")
    
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            print(f"👤 USER:\n{msg.content}\n")
        
        elif isinstance(msg, AIMessage):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"🤖 AGENT (Calling Tools):")
                for tool_call in msg.tool_calls:
                    print(f"  🔧 {tool_call['name']}")
                    print(f"     Args: {json.dumps(tool_call['args'], indent=6)}\n")
            else:
                print(f"🤖 AGENT FINAL ANALYSIS:\n{msg.content}\n")
        
        elif hasattr(msg, "content"):
            try:
                content = json.loads(msg.content)
                if content.get("status") == "success":
                    print(f"✅ TOOL RESULT: Found {content.get('count')} articles\n")
            except:
                pass


if __name__ == "__main__":
    # Initialize agent
    agent = NewsGathererAgent()
    print("Generating workflow graph...")
    agent.visualize_graph("workflow_graph.png")
    print("Graph saved to: workflow_graph.png\n")
    # Example 1: AI Technology
    print("\n🚀 EXAMPLE 1: AI Technology News")
    result1 = agent.run(
        user_request="Get the latest breakthrough news in artificial intelligence "
                    "from the United States. Focus on major developments from "
                    "leading tech companies and research institutions.",
        top_articles=5
    )
    print_results(result1)
    
    
    # Example 2: Sports
    print("\n\n🚀 EXAMPLE 2: Sports News")
    result2 = agent.run(
        user_request="Find recent news about Cristiano Ronaldo. I want stories "
                    "with good depth and interesting content.",
        top_articles=3
    )
    print_results(result2)