"""
Main Streamlit application for Mutual Fund FAQ Chatbot
Entry point for the application
"""

import streamlit as st
import sys
import os
import csv
import uuid
import time
import json
import io
from dotenv import load_dotenv

# Load environment variables from .env (local) or Streamlit secrets (cloud)
# Try Streamlit secrets first (for deployment)
try:
    # If running on Streamlit Cloud, load secrets into environment
    if hasattr(st, 'secrets'):
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
except Exception:
    pass

# Load from .env file (for local development)
load_dotenv()

# Trace logging configuration
LOG_TRACES = os.getenv("LOG_TRACES", "false").lower() == "true"
LOG_CSV_PATH = os.getenv("LOG_CSV_PATH", "logs/traces.csv")
# Ensure directory exists if a directory is specified
log_dir = os.path.dirname(LOG_CSV_PATH)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)

# Google Drive configuration (optional)
GDRIVE_JSON = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON", "")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID", "")
UPLOAD_TO_GDRIVE = os.getenv("UPLOAD_TO_GDRIVE", "false").lower() == "true"

# Lazy imports for Google Drive client
def _get_drive_service():
    """Get Google Drive service with detailed error reporting"""
    # Check environment variables
    if not GDRIVE_JSON:
        return None, "GDRIVE_SERVICE_ACCOUNT_JSON environment variable is not set"
    if not GDRIVE_FOLDER_ID:
        return None, "GDRIVE_FOLDER_ID environment variable is not set"
    
    # Check library imports
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:
        return None, f"Google libraries not installed. Install with: pip install google-api-python-client google-auth. Error: {str(e)}"
    
    # Parse JSON and create credentials
    json_to_parse = GDRIVE_JSON.strip()
    
    try:
        creds_info = json.loads(json_to_parse)
    except json.JSONDecodeError as e:
        error_msg = str(e)
        suggestion = ""
        if "control character" in error_msg.lower():
            suggestion = (
                "\n\nTIP: Your JSON contains unescaped control characters (newlines/tabs). "
                "For environment variables, the JSON must be a single-line string.\n"
                "Solutions:\n"
                "1. Run 'python fix_gdrive_json.py' to format your JSON correctly\n"
                "2. Or manually: Copy your JSON file content and use json.dumps() to convert it to a single line\n"
                "3. In .env file, ensure the entire JSON is on ONE line with escaped quotes"
            )
        return None, f"Invalid JSON in GDRIVE_SERVICE_ACCOUNT_JSON: {error_msg}{suggestion}"
    
    try:
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive.file"]
        )
        drive_service = build("drive", "v3", credentials=creds)
        return drive_service, None
    except Exception as e:
        return None, f"Error creating Drive service: {str(e)}"


def upload_log_to_gdrive(local_path: str, drive_filename: str):
    """
    Upload a local file to Google Drive (requires service account JSON and folder ID).
    Returns (success: bool, message: str) tuple with detailed error messages.
    """
    # Get drive service with error details
    result = _get_drive_service()
    if isinstance(result, tuple):
        drive_service, error = result
        if not drive_service:
            return False, error or "Drive service not configured or libraries missing"
    else:
        # Backward compatibility
        drive_service = result
        if not drive_service:
            return False, "Drive service not configured or libraries missing"
    
    # Check if file exists
    if not os.path.exists(local_path):
        return False, f"Local log file not found: {local_path}"
    
    # Check file size
    file_size = os.path.getsize(local_path)
    if file_size == 0:
        return False, f"Log file is empty: {local_path}"

    try:
        from googleapiclient.http import MediaIoBaseUpload
        file_metadata = {"name": drive_filename, "parents": [GDRIVE_FOLDER_ID]}
        
        # Open file and create media upload
        with open(local_path, "rb") as f:
            media = MediaIoBaseUpload(f, mimetype="text/csv", resumable=True)
            drive_service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
        
        return True, f"Successfully uploaded {drive_filename} ({file_size:,} bytes) to Google Drive"
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error messages
        if "insufficient authentication scopes" in error_msg.lower():
            return False, f"Authentication error: Service account needs 'drive.file' scope. Error: {error_msg}"
        elif "not found" in error_msg.lower() or "404" in error_msg:
            return False, f"Folder not found: Check if GDRIVE_FOLDER_ID ({GDRIVE_FOLDER_ID[:20]}...) is correct and service account has access. Error: {error_msg}"
        else:
            return False, f"Upload failed: {error_msg}"


def log_trace_csv(trace_text: str, user_input: str, llm_response: str):
    """
    Append a trace row to CSV for eval/error analysis.

    Columns:
    - trace_id
    - trace        (free-form info, e.g., timestamp/classification)
    - user_input
    - llm_response
    """
    if not LOG_TRACES:
        return

    row = {
        "trace_id": str(uuid.uuid4()),
        "trace": trace_text,
        "user_input": user_input,
        "llm_response": llm_response,
    }

    file_exists = os.path.exists(LOG_CSV_PATH)
    with open(LOG_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    # Optional: auto-upload to Google Drive if enabled
    if UPLOAD_TO_GDRIVE:
        upload_log_to_gdrive(LOG_CSV_PATH, "traces.csv")

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Groww Mutual Fund Chatbot",
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
        # Check if we have a pre-computed answer for this example question
        if 'example_question_answer' in st.session_state:
            answer_data = st.session_state.example_question_answer
            # Add the answer directly to chat history
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': example_question,
                'source_url': None
            })
            
            # Add bot message with pre-computed answer
            st.session_state.chat_history.append({
                'role': 'bot',
                'content': answer_data['answer'],
                'source_url': answer_data['source_url']
            })
            
            # Clear the example question answer from session state
            del st.session_state.example_question_answer
            
            # Don't process through pipeline, just return None to trigger rerun
            st.rerun()
            return None
        
        return example_question
    
    # Get input from chat UI
    from frontend.components.chat_ui import render_input_area
    user_input, send_clicked = render_input_area()
    
    # Return input only if send button was clicked and input is not empty
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
    from backend.validators import ValidationResult
    from config import SYSTEM_PROMPT, EXAMPLE_QUESTION_SYSTEM_PROMPT, RETRIEVAL_CONFIG
    from frontend.components.welcome import EXAMPLE_QUESTIONS
    import logging
    
    logger = logging.getLogger(__name__)
    
    logger.info(f"[QUERY PROCESSING] Starting query processing for: '{query}'")
    
    # Detect if this is an example question (normalize for comparison)
    normalized_query = query.strip()
    is_example_question = normalized_query in EXAMPLE_QUESTIONS
    logger.debug(f"[QUERY PROCESSING] Is example question: {is_example_question}")
    
    # Step 1: Preprocess query
    logger.info("[QUERY PROCESSING] Step 1: Preprocessing query...")
    preprocessed = preprocess_query(query)
    classification = preprocessed['classification']
    scheme_name = preprocessed.get('scheme_name')
    precomputed_response = preprocessed.get('precomputed_response')
    logger.info(f"[QUERY PROCESSING] Classification: {classification}, Scheme: {scheme_name}, Has precomputed: {bool(precomputed_response)}")
    trace_text = f"ts={int(time.time())};class={classification};scheme={scheme_name or 'none'}"
    
    # Step 2: Check for precomputed response (advice, jailbreak, non-MF, scheme not available)
    if precomputed_response:
        logger.info(f"[QUERY PROCESSING] Step 2: Using precomputed response (type: {classification})")
        return format_response(
            answer=precomputed_response.get('answer', ''),
            source_url=precomputed_response.get('source_url', ''),
            query=query,
            scheme_name=scheme_name
        )
    
    # Step 3: Retrieve chunks (only for factual queries)
    if classification != 'factual':
        logger.warning(f"[QUERY PROCESSING] Step 3: Non-factual classification '{classification}' - using fallback")
        return format_fallback_response(query, scheme_name)
    
    logger.info(f"[QUERY PROCESSING] Step 3: Retrieving chunks (top_k={RETRIEVAL_CONFIG.get('top_k', 3)}, scheme={scheme_name})...")
    chunks = retrieval_system.retrieve(
        query=preprocessed['expanded_query'],
        top_k=RETRIEVAL_CONFIG.get("top_k", 3),  # Use optimized top_k from config
        scheme_name=scheme_name,
        include_metadata=True
    )
    logger.info(f"[QUERY PROCESSING] Retrieved {len(chunks)} chunks")
    
    if not chunks:
        logger.warning("[QUERY PROCESSING] No chunks retrieved - using fallback response")
        return format_fallback_response(query, scheme_name)
    
    # Log chunk details
    for i, chunk in enumerate(chunks[:3], 1):  # Log top 3 chunks
        logger.debug(f"[QUERY PROCESSING] Chunk {i}: scheme={chunk.get('scheme_name')}, score={chunk.get('reranked_score', chunk.get('score', 0)):.4f}, has_text={bool(chunk.get('text'))}")

    # Step 4: Prepare context (optimized for token efficiency)
    max_chunks = RETRIEVAL_CONFIG.get("top_k", 3)  # Use same as top_k
    max_context_tokens = RETRIEVAL_CONFIG.get("max_context_tokens", 800)
    logger.info(f"[QUERY PROCESSING] Step 4: Preparing context (max_chunks={max_chunks}, max_tokens={max_context_tokens})...")
    context_dict = retrieval_system.prepare_context(
        chunks, 
        max_chunks=max_chunks,
        max_context_tokens=max_context_tokens
    )
    context = context_dict['context']
    source_urls = context_dict['source_urls']
    primary_source_url = source_urls[0] if source_urls else None
    logger.info(f"[QUERY PROCESSING] Context prepared: {len(context)} chars, {len(source_urls)} source URLs, chunks_used={context_dict.get('num_chunks', 0)}")

    # Step 5: Format user prompt
    logger.info("[QUERY PROCESSING] Step 5: Formatting user prompt...")
    user_prompt = llm_service.format_user_prompt(context, query)
    logger.debug(f"[QUERY PROCESSING] User prompt length: {len(user_prompt)} chars")

    # Step 6: Choose system prompt based on query type
    # Use example question prompt for example questions
    system_prompt_to_use = EXAMPLE_QUESTION_SYSTEM_PROMPT if is_example_question else SYSTEM_PROMPT
    logger.debug(f"[QUERY PROCESSING] Step 6: Using {'example' if is_example_question else 'standard'} system prompt")

    # Step 7: Generate validated response
    logger.info("[QUERY PROCESSING] Step 7: Generating validated response...")
    validated_response, validation_result = llm_service.generate_validated_response(
        system_prompt=system_prompt_to_use,
        user_prompt=user_prompt,
        query=query,
        source_url=primary_source_url,
        scheme_name=scheme_name,
        max_retries=3,
        use_fallback=True
    )
    logger.info(f"[QUERY PROCESSING] Response generated: length={len(validated_response) if validated_response else 0} chars, valid={validation_result.is_valid if hasattr(validation_result, 'is_valid') else 'unknown'}")
    if hasattr(validation_result, 'errors') and validation_result.errors:
        logger.warning(f"[QUERY PROCESSING] Validation errors: {validation_result.errors}")
    if hasattr(validation_result, 'fixes_applied') and validation_result.fixes_applied:
        logger.info(f"[QUERY PROCESSING] Fixes applied: {validation_result.fixes_applied}")
    
    # Step 9: Format response
    logger.info("[QUERY PROCESSING] Step 8: Formatting final response...")
    formatted_response = format_response(
        answer=validated_response,
        source_url=primary_source_url,
        validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
        query=query,
        scheme_name=scheme_name
    )
    logger.info(f"[QUERY PROCESSING] Query processing complete. Response ready with source_url={bool(formatted_response.get('source_url'))}")

    # Log to CSV for evals
    log_trace_csv(
        trace_text=trace_text,
        user_input=query,
        llm_response=formatted_response.get("answer", "")
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
    
    # Show title at the top (centered, full width)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 30px;'>
                <h1 style='color: #10B981; margin-bottom: 10px; font-size: 2.5rem; font-weight: 700;'>Groww Mutual Fund Chatbot</h1>
                <p style='color: #6B7280; font-size: 16px; margin-top: 8px;'>Your trusted partner for factual information</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
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
            # Ensure source_url is not None or empty string
            source_url = formatted_response.get('source_url', '').strip() if formatted_response.get('source_url') else None
            add_message_to_history(
                'bot',
                formatted_response.get('answer', ''),
                source_url=source_url if source_url else None
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
            # Log error trace
            log_trace_csv(
                trace_text=f"ERROR ts={int(time.time())}",
                user_input=query,
                llm_response=f"ERROR: {e}"
            )
        finally:
            # Clear processing flag
            st.session_state.processing = False
            st.rerun()
    
    # Create two-column layout: Left (schemes + examples) | Right (chatbot)
    left_col, right_col = st.columns([1, 1.5], gap="medium")
    
    # LEFT QUADRANT: Available Schemes + Example Questions
    with left_col:
        st.markdown("<div style='margin-top: 0;'>", unsafe_allow_html=True)
        from frontend.components.welcome import render_schemes_section, render_example_questions
        render_schemes_section()
        st.markdown("<br>", unsafe_allow_html=True)
        render_example_questions()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # RIGHT QUADRANT: Chatbot Interface
    with right_col:
        st.markdown("<div style='margin-top: 0; padding: 0;'>", unsafe_allow_html=True)
        # Display chat history if exists
        if st.session_state.chat_history:
            from frontend.components.chat_ui import render_chat_history
            render_chat_history(st.session_state.chat_history)
        else:
            # Show placeholder when no chat history
            st.markdown(
                """
                <div style='text-align: center; padding: 40px 20px; color: #9CA3AF;'>
                    <h3 style='color: #6B7280; font-size: 1.2rem; margin-bottom: 8px;'>👋 Welcome!</h3>
                    <p style='font-size: 0.95rem;'>Ask me anything about SBI Mutual Funds</p>
                    <p style='font-size: 0.85rem; margin-top: 12px;'>Try the example questions or type your own below</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Show loading indicator if processing
        if st.session_state.processing:
            from frontend.components.chat_ui import render_loading_indicator
            render_loading_indicator()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Get user input (positioned in right column below chat/welcome)
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
    
    # Sidebar: manual upload of logs to Google Drive (when enabled)
    with st.sidebar:
        if LOG_TRACES and os.path.exists(LOG_CSV_PATH):
            if st.button("Upload traces to Google Drive", type="primary"):
                ok, msg = upload_log_to_gdrive(LOG_CSV_PATH, "traces.csv")
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        if LOG_TRACES:
            st.markdown("#### Logs & Drive")
            st.caption(f"Upload enabled: {UPLOAD_TO_GDRIVE}, Path: {LOG_CSV_PATH}")
            
            # Diagnostic information
            with st.expander("🔍 Configuration Diagnostics", expanded=False):
                # Check environment variables
                st.write("**Environment Variables:**")
                st.caption(f"GDRIVE_SERVICE_ACCOUNT_JSON: {'✓ Set' if GDRIVE_JSON else '✗ Not Set'}")
                st.caption(f"GDRIVE_FOLDER_ID: {'✓ Set' if GDRIVE_FOLDER_ID else '✗ Not Set'}")
                if GDRIVE_FOLDER_ID:
                    st.caption(f"Folder ID: {GDRIVE_FOLDER_ID[:30]}...")
                
                # Check libraries
                try:
                    from google.oauth2 import service_account
                    from googleapiclient.discovery import build
                    st.write("**Libraries:**")
                    st.caption("✓ Google libraries installed")
                except ImportError:
                    st.write("**Libraries:**")
                    st.caption("✗ Google libraries missing - install with: pip install google-api-python-client google-auth")
                
                # Check file
                st.write("**Log File:**")
                if os.path.exists(LOG_CSV_PATH):
                    file_size = os.path.getsize(LOG_CSV_PATH)
                    st.caption(f"✓ File exists: {LOG_CSV_PATH}")
                    st.caption(f"✓ Size: {file_size:,} bytes")
                else:
                    st.caption(f"✗ File not found: {LOG_CSV_PATH}")
                
                # Test drive service
                if st.button("Test Drive Service", type="secondary"):
                    result = _get_drive_service()
                    if isinstance(result, tuple):
                        service, error = result
                        if service:
                            st.success("✓ Drive service initialized successfully")
                        else:
                            st.error(f"✗ {error}")
                    else:
                        if result:
                            st.success("✓ Drive service initialized successfully")
                        else:
                            st.error("✗ Drive service initialization failed")
            
            if st.button("Test Drive upload (diagnose)"):
                # Ensure there is a file to upload
                if not os.path.exists(LOG_CSV_PATH):
                    os.makedirs(os.path.dirname(LOG_CSV_PATH) or ".", exist_ok=True)
                    sample_row = {
                        "trace_id": str(uuid.uuid4()),
                        "trace": "diagnostic",
                        "user_input": "diagnostic user input",
                        "llm_response": "diagnostic llm response",
                    }
                    file_exists = False
                    with open(LOG_CSV_PATH, "a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=sample_row.keys())
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow(sample_row)
                    st.info(f"Created test file: {LOG_CSV_PATH}")
                
                ok, msg = upload_log_to_gdrive(LOG_CSV_PATH, "traces.csv")
                if ok:
                    st.success(f"Diagnostic upload success: {msg}")
                else:
                    st.error(f"Diagnostic upload failed: {msg}")
    
    # Add clear chat button in sidebar
    with st.sidebar:
        st.markdown("### Settings")
        if st.button("Clear Chat History", type="secondary"):
            from frontend.components.chat_ui import clear_chat_history
            clear_chat_history()
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
    
    # Render footer (disclaimer) - always at bottom, full width
    st.markdown("<br>", unsafe_allow_html=True)
    from frontend.components.footer import render_footer
    render_footer()

if __name__ == "__main__":
    main()

