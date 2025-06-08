"""
Test script to verify agent workflow with real prompts.
"""

import json
from typing import Dict, Any
from pathlib import Path

from agents.content import ContentAgent
from agents.image import ImageAgent
from agents.research import ResearchAgent
from models.schema import Platform, Tone, ResearchRequest

def test_workflow():
    # Create test directories if they don't exist
    Path('data/images').mkdir(parents=True, exist_ok=True)
    
    print("\n1. Testing ResearchAgent...")
    research_agent = ResearchAgent()
    
    # Sample research request
    research_request = ResearchRequest(
        topic="The future of artificial intelligence in healthcare",
        platform=Platform.MEDIUM,
        tone=Tone.INFORMATIVE
    )
    
    # Run research
    print(f"Researching: {research_request.topic}")
    research_result = research_agent.research(research_request)
    
    # Display research results
    print("\nResearch Results:")
    for i, point in enumerate(research_result.bullet_points, 1):
        print(f"{i}. {point.content}")
    
    # Initialize state for workflow
    state: Dict[str, Any] = {
        "topic": research_request.topic,
        "platform": research_request.platform,
        "tone": research_request.tone,
        "research_result": research_result
    }
    
    print("\n2. Testing ContentAgent...")
    content_agent = ContentAgent()
    state = content_agent.run(state)
    
    print("\nGenerated Content:")
    print(f"Title: {state['content_result'].title}")
    print(f"Content:\n{state['content_result'].content}")
    
    print("\n3. Testing ImageAgent...")
    image_agent = ImageAgent()
    state = image_agent.run(state)
    
    print("\nGenerated Image Prompt:")
    print(state['image_result'].image_prompt)
    print(f"Image saved at: {state['image_result'].image_path}")
    
    print("\nFull workflow test completed successfully!")
    
    # Save the final state for reference
    with open('test_results.json', 'w') as f:
        json_state = {k: str(v) for k, v in state.items()}
        json.dump(json_state, f, indent=2)
    
    print("Test results saved to test_results.json")

if __name__ == "__main__":
    test_workflow()
