"""
Main Streamlit application for Mutual Fund FAQ Chatbot
Entry point for the application
"""

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="SBI Mutual Fund FAQ Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def initialize_session_state():
    """
    Initialize all session state variables
    """
    # Chat history - list of message dictionaries
    # Each message: {'role': 'user'|'bot', 'content': str, 'source_url': str|None}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Track if app has been initialized
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    
    # Store example question from welcome component
    if 'example_question' not in st.session_state:
        st.session_state.example_question = None
    
    # Track if processing is in progress
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Store last user input (for handling example questions)
    if 'last_user_input' not in st.session_state:
        st.session_state.last_user_input = ""


def get_user_input():
    """
    Get user input, handling example questions from welcome component
    
    Returns:
        User input string or None
    """
    from frontend.components.welcome import get_example_question
    
    # Check if example question was clicked
    example_question = get_example_question()
    if example_question:
        return example_question
    
    # Get input from chat UI
    from frontend.components.chat_ui import render_input_area
    user_input, send_clicked = render_input_area()
    
    if send_clicked and user_input:
        return user_input.strip()
    
    return None


def initialize_backend_services():
    """
    Initialize backend services (LLM, Retrieval)
    
    Returns:
        Tuple of (llm_service, retrieval_system) or (None, None) if initialization fails
    """
    try:
        from backend.llm_service import get_llm_service
        from backend.retrieval import get_retrieval_system
        
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        
        return llm_service, retrieval_system
    except Exception as e:
        st.error(f"Failed to initialize backend services: {e}")
        return None, None


def process_query(query: str, llm_service, retrieval_system):
    """
    Process user query through the full pipeline:
    1. Query preprocessing
    2. Check for precomputed responses (advice, jailbreak, non-MF)
    3. Retrieve chunks (if factual)
    4. Generate response with LLM
    5. Format response
    
    Args:
        query: User query string
        llm_service: LLMService instance
        retrieval_system: RetrievalSystem instance
        
    Returns:
        Formatted response dictionary
    """
    from backend.query_processor import preprocess_query
    from backend.formatter import format_response, format_fallback_response
    from config import SYSTEM_PROMPT
    
    # Step 1: Preprocess query
    preprocessed = preprocess_query(query)
    classification = preprocessed['classification']
    scheme_name = preprocessed.get('scheme_name')
    precomputed_response = preprocessed.get('precomputed_response')
    
    # Step 2: Check for precomputed response (advice, jailbreak, non-MF, scheme not available)
    if precomputed_response:
        return format_response(
            answer=precomputed_response.get('answer', ''),
            source_url=precomputed_response.get('source_url', ''),
            query=query,
            scheme_name=scheme_name
        )
    
    # Step 3: Retrieve chunks (only for factual queries)
    if classification != 'factual':
        # Should not happen, but handle gracefully
        return format_fallback_response(query, scheme_name)
    
    chunks = retrieval_system.retrieve(
        query=preprocessed['expanded_query'],
        top_k=5,
        scheme_name=scheme_name,
        include_metadata=True
    )
    
    if not chunks:
        # No chunks retrieved - use fallback
        return format_fallback_response(query, scheme_name)
    
    # Step 4: Prepare context
    context_dict = retrieval_system.prepare_context(chunks, max_chunks=5)
    context = context_dict['context']
    source_urls = context_dict['source_urls']
    primary_source_url = source_urls[0] if source_urls else None
    
    # Step 5: Format user prompt
    user_prompt = llm_service.format_user_prompt(context, query)
    
    # Step 6: Generate validated response
    validated_response, validation_result = llm_service.generate_validated_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        query=query,
        source_url=primary_source_url,
        scheme_name=scheme_name,
        max_retries=3,
        use_fallback=True
    )
    
    # Step 7: Format response
    formatted_response = format_response(
        answer=validated_response,
        source_url=primary_source_url,
        validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
        query=query,
        scheme_name=scheme_name
    )
    
    return formatted_response


# Initialize session state
initialize_session_state()

# Main app
def main():
    """Main application function"""
    
    # Load CSS
    try:
        with open('frontend/styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Styling may not be applied.")
    
    # Title
    st.title("💬 SBI Mutual Fund FAQ Chatbot")
    st.markdown("Ask questions about SBI Mutual Fund schemes")
    
    # Show welcome section if no chat history
    if not st.session_state.chat_history:
        from frontend.components.welcome import render_welcome
        render_welcome()
        st.markdown("---")
    
    # Display chat history
    if st.session_state.chat_history:
        from frontend.components.chat_ui import render_chat_history
        render_chat_history(st.session_state.chat_history)
    
    # Show loading indicator if processing
    if st.session_state.processing:
        from frontend.components.chat_ui import render_loading_indicator
        render_loading_indicator()
    
    # Initialize backend services (singleton pattern - cached in session state)
    if 'llm_service' not in st.session_state or 'retrieval_system' not in st.session_state:
        with st.spinner("Initializing services..."):
            llm_service, retrieval_system = initialize_backend_services()
            if llm_service and retrieval_system:
                st.session_state.llm_service = llm_service
                st.session_state.retrieval_system = retrieval_system
            else:
                st.error("Failed to initialize backend services. Please check your environment variables.")
                st.stop()
    
    # Process query if processing flag is set (from previous rerun)
    if st.session_state.processing and 'pending_query' in st.session_state:
        query = st.session_state.pending_query
        del st.session_state.pending_query
        
        try:
            # Process query through backend
            with st.spinner("Processing your query..."):
                formatted_response = process_query(
                    query,
                    st.session_state.llm_service,
                    st.session_state.retrieval_system
                )
            
            # Add bot response to history
            from frontend.components.chat_ui import add_message_to_history
            add_message_to_history(
                'bot',
                formatted_response.get('answer', ''),
                source_url=formatted_response.get('source_url')
            )
            
        except Exception as e:
            # Handle errors gracefully
            st.error(f"An error occurred: {e}")
            from backend.formatter import format_error_response
            error_response = format_error_response(
                f"I apologize, but an error occurred while processing your query. Please try again.",
                query=query
            )
            from frontend.components.chat_ui import add_message_to_history
            add_message_to_history(
                'bot',
                error_response.get('answer', ''),
                source_url=error_response.get('source_url')
            )
        finally:
            # Clear processing flag
            st.session_state.processing = False
            st.rerun()
    
    # Get user input
    user_input = get_user_input()
    
    # Handle user input
    if user_input:
        # Add user message to history
        from frontend.components.chat_ui import add_message_to_history
        add_message_to_history('user', user_input)
        
        # Store query for processing and mark as processing
        st.session_state.pending_query = user_input
        st.session_state.processing = True
        st.rerun()
    
    # Add clear chat button in sidebar
    with st.sidebar:
        st.markdown("### Settings")
        if st.button("Clear Chat History", type="secondary"):
            from frontend.components.chat_ui import clear_chat_history
            clear_chat_history()
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
    
    # Render footer
    from frontend.components.footer import render_footer
    render_footer()

if __name__ == "__main__":
    main()

