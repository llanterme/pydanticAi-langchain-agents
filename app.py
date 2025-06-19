"""
Streamlit application for the multi-agent LLM system.

This module provides a web interface for users to interact with the content generation workflow,
allowing them to specify topic, platform, and tone for content generation.
"""

import os
import asyncio
import time
from pathlib import Path
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from models.schema import Platform, Tone, ContentResponse
from flow.graph import create_workflow_graph, WorkflowState
from agents.linkedin import LinkedInAgent


def initialize_app():
    """Initialize the application and set up the page configuration."""
    st.set_page_config(
        page_title="AI Content Generator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("AI Content Generator")
    st.write("Generate content and images using advanced AI agents.")


def validate_environment():
    """
    Validate that required environment variables are set.
    
    Returns:
        Error message if validation fails, None otherwise.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY environment variable is not set. Please create a .env file with this key."
    return None


def post_to_linkedin(content_text, title=None):
    """
    Post content to LinkedIn.
    
    Args:
        content_text: The content text to post
        title: Optional title for the post
        
    Returns:
        Success status and message
    """
    print("\n===== LINKEDIN POSTING FUNCTION STARTED =====")
    print(f"Content length: {len(content_text)}, Has title: {title is not None}")
    
    try:
        # Check if LinkedIn access token is available
        token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        print(f"LinkedIn access token available: {bool(token)}")
        
        if not token:
            print("Error: LinkedIn access token not found")
            return False, "LinkedIn access token not found. Please set LINKEDIN_ACCESS_TOKEN environment variable."
        
        print("Creating ContentResponse object")
        # Create ContentResponse object
        content_response = ContentResponse(content=content_text, title=title)
        
        print("Creating LinkedIn agent")
        # Create LinkedIn agent and post content
        linkedin_agent = LinkedInAgent()
        
        # Run the async function synchronously
        print("Setting up asyncio event loop")
        try:
            loop = asyncio.get_event_loop()
            print("Got existing event loop")
        except RuntimeError as e:
            print(f"Creating new event loop due to: {str(e)}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        print("Calling linkedin_agent.post_content")
        result = loop.run_until_complete(linkedin_agent.post_content(content_response))
        print(f"LinkedIn post result: success={result.success}, error={result.error_message if hasattr(result, 'error_message') else None}")
        
        if result.success:
            message = f"Successfully posted to LinkedIn!"
            if result.post_id:
                message += f" Post ID: {result.post_id}"
            if result.post_url:
                message += f" URL: {result.post_url}"
            print(f"Success message: {message}")
            return True, message
        else:
            error_msg = f"Failed to post to LinkedIn: {result.error_message}"
            print(f"Error message: {error_msg}")
            return False, error_msg
        
    except Exception as e:
        import traceback
        print(f"Exception in post_to_linkedin: {str(e)}")
        print(traceback.format_exc())
        return False, f"Failed to post to LinkedIn: {str(e)}"


def user_input_form():
    """
    Create a form for user input.
    
    Returns:
        Dictionary with user inputs if form is submitted, None otherwise.
    """
    with st.form("content_generation_form"):
        col1, col2 = st.columns(2)

        with col1:
            topic = st.text_input(
                "Topic", 
                placeholder="e.g., artificial intelligence ethics",
                help="Enter the subject you want to generate content about"
            )
            platform = st.selectbox(
                "Platform",
                options=[p.value for p in Platform],
                format_func=lambda x: x.capitalize(),
                help="Select the platform where your content will be published"
            )

        with col2:
            tone = st.selectbox(
                "Tone",
                options=[t.value for t in Tone],
                format_func=lambda x: x.capitalize(),
                help="Select the style and mood for your content"
            )
            
        submit_button = st.form_submit_button("Generate Content")
        
        if submit_button and topic:
            return {
                "topic": topic,
                "platform": platform,
                "tone": tone
            }
        elif submit_button and not topic:
            st.error("Please enter a topic before generating content.")
            
        return None


def run_workflow(inputs):
    """
    Run the multi-agent workflow with the user inputs.
    
    Args:
        inputs: Dictionary containing user inputs.
        
    Returns:
        Final workflow state with results.
    """
    # Create initial state for workflow
    initial_state: WorkflowState = {
        "topic": inputs["topic"],
        "platform": Platform(inputs["platform"]),
        "tone": Tone(inputs["tone"]),
    }
    
    # Create and execute the workflow
    workflow = create_workflow_graph()
    
    with st.spinner("Generating content and image... This may take a minute or two."):
        # Execute the workflow and get the final state
        final_state = workflow.invoke(initial_state)
        
    return final_state


def display_results(state):
    """
    Display the workflow results in the Streamlit UI.
    
    Args:
        state: Final workflow state with results.
    """
    platform = state["platform"].value
    content = state["content_result"]
    image_result = state.get("image_result")
    
    st.success("Content generated successfully!")
    
    # Add LinkedIn posting section if platform is LinkedIn
    if state["platform"] == Platform.LINKEDIN:
        st.markdown("---")
        st.subheader("LinkedIn Posting")
        
        # Initialize session state keys if they don't exist
        if 'post_to_linkedin' not in st.session_state:
            st.session_state.post_to_linkedin = False
        if 'linkedin_result' not in st.session_state:
            st.session_state.linkedin_result = None
        
        # Check if we need to process a LinkedIn post
        if st.session_state.post_to_linkedin and st.session_state.linkedin_result is None:
            with st.spinner("Posting to LinkedIn..."):
                try:
                    # Check token
                    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
                    if not token:
                        st.session_state.linkedin_result = {
                            'success': False,
                            'message': "LinkedIn access token not found. Please set LINKEDIN_ACCESS_TOKEN environment variable."
                        }
                    else:
                        # Post to LinkedIn
                        success, message = post_to_linkedin(
                            content.content, 
                            title=content.title if content.title else None
                        )
                        st.session_state.linkedin_result = {
                            'success': success,
                            'message': message
                        }
                        
                except Exception as e:
                    st.session_state.linkedin_result = {
                        'success': False,
                        'message': f"Error: {str(e)}"
                    }
        
        # Display results if available
        if st.session_state.linkedin_result:
            if st.session_state.linkedin_result['success']:
                st.success(f"✅ {st.session_state.linkedin_result['message']}")
            else:
                st.error(f"❌ {st.session_state.linkedin_result['message']}")
            
            # Reset button
            if st.button("🔄 Post Again", type="secondary", key="post_again"):
                st.session_state.post_to_linkedin = False
                st.session_state.linkedin_result = None
                st.rerun()
        else:
            # Post button
            if st.button("📤 Post to LinkedIn", type="primary", key="post_linkedin"):
                st.session_state.post_to_linkedin = True
                st.rerun()
        
        st.markdown("---")
    
    # Create tabs to organize results
    tab1, tab2, tab3 = st.tabs(["Generated Content", "Image", "Research Notes"])
    
    # Content tab
    with tab1:
        st.subheader(f"{platform.capitalize()} Content")
        
        if content.title:
            st.markdown(f"### {content.title}")
            
        st.write(content.content)
        
        tone = state["tone"].value
        st.caption(f"Generated with a {tone} tone for {platform}")
        
    # Image tab
    with tab2:
        if image_result and Path(str(image_result.image_path)).exists():
            st.subheader("Generated Image")
            
            # Display the image
            image = Image.open(image_result.image_path)
            st.image(image, caption=f"Generated for {platform} content", use_container_width=True)
            
            with st.expander("Image Generation Prompt"):
                st.write(image_result.image_prompt)
        else:
            st.warning("No image was generated or the image file was not found.")
            
    # Research tab        
    with tab3:
        st.subheader("Research Bullet Points")
        
        research = state.get("research_result")
        if research and research.bullet_points:
            for i, point in enumerate(research.bullet_points, 1):
                st.markdown(f"{i}. {point.content}")
        else:
            st.info("No research data available.")


def main():
    """Main function to run the Streamlit app."""
    # Load environment variables
    load_dotenv()
    
    # Initialize the app
    initialize_app()
    
    # Validate environment
    error = validate_environment()
    if error:
        st.error(error)
        return
    
    # Initialize session state for workflow results
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    
    # Get user input
    inputs = user_input_form()
    
    # Run workflow if NEW inputs are provided
    if inputs:
        try:
            # Reset LinkedIn posting state for new content generation
            st.session_state.post_to_linkedin = False
            st.session_state.linkedin_result = None
            
            # Run the workflow and store results in session state
            st.session_state.workflow_results = run_workflow(inputs)
                
        except Exception as e:
            st.error(f"Error during content generation: {str(e)}")
            st.exception(e)
            return
    
    # Display results if they exist (either from new generation or previous session)
    if st.session_state.workflow_results:
        try:
            display_results(st.session_state.workflow_results)
        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()