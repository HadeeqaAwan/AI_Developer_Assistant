import streamlit as st
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Developer Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# API CONFIGURATION
# ============================================================

API_BASE_URL = "https://ai-developer-assistant-0kbj.onrender.com"


# ============================================================
# SESSION STATE
# ============================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "documents" not in st.session_state:
    st.session_state.documents = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def load_conversations():

    try:

        response = requests.get(
            f"{API_BASE_URL}/conversations/",
            headers=get_headers(),
            timeout=30
        )

        response.raise_for_status()

        st.session_state.conversations = response.json()

    except Exception:

        st.session_state.conversations = []


def load_documents():

    try:

        response = requests.get(
            f"{API_BASE_URL}/documents/",
            headers=get_headers(),
            timeout=30
        )

        response.raise_for_status()

        st.session_state.documents = response.json()

    except Exception:

        st.session_state.documents = []


def load_messages(conversation_id):

    try:

        response = requests.get(
            f"{API_BASE_URL}/conversations/"
            f"{conversation_id}/messages",
            headers=get_headers(),
            timeout=30
        )

        response.raise_for_status()

        messages = response.json()

        st.session_state.messages = [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in messages
            if message["role"] in ["user", "assistant"]
        ]

    except Exception as e:

        st.error(
            f"Could not load conversation: {str(e)}"
        )


def create_conversation():

    try:

        response = requests.post(
            f"{API_BASE_URL}/conversations/",
            headers=get_headers(),
            json={
                "title": "New Conversation"
            },
            timeout=30
        )

        response.raise_for_status()

        conversation = response.json()

        st.session_state.conversation_id = conversation["id"]

        st.session_state.messages = []

        load_conversations()

        return True

    except Exception as e:

        st.error(
            f"Could not create conversation: {str(e)}"
        )

        return False


def update_conversation_title(
    conversation_id,
    title
):

    try:

        response = requests.patch(
            f"{API_BASE_URL}/conversations/"
            f"{conversation_id}",
            headers=get_headers(),
            json={
                "title": title
            },
            timeout=30
        )

        response.raise_for_status()

        return True

    except Exception:

        return False


def get_display_name(email):

    if not email:
        return "User"

    name = email.split("@")[0]

    name = name.replace(".", " ")
    name = name.replace("_", " ")
    name = name.replace("-", " ")

    return name.title()


# ============================================================
# LOGIN / REGISTER SCREEN
# ============================================================

if not st.session_state.token:

    st.title("AI Developer Assistant")

    st.caption(
        "Multi-agent development assistant powered by "
        "LangGraph and Gemini."
    )

    st.divider()

    tab1, tab2 = st.tabs(
        ["Login", "Register"]
    )


    # ========================================================
    # LOGIN
    # ========================================================

    with tab1:

        st.subheader("Login")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not login_email or not login_password:

                st.warning(
                    "Please enter your email and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={
                            "email": login_email,
                            "password": login_password
                        },
                        timeout=30
                    )

                    response.raise_for_status()

                    data = response.json()

                    st.session_state.token = (
                        data["access_token"]
                    )

                    st.session_state.user_email = (
                        login_email
                    )

                    load_conversations()
                    load_documents()

                    if st.session_state.conversations:

                        first_conversation = (
                            st.session_state.conversations[-1]
                        )

                        st.session_state.conversation_id = (
                            first_conversation["id"]
                        )

                        load_messages(
                            first_conversation["id"]
                        )

                    else:

                        create_conversation()

                    st.rerun()

                except requests.exceptions.HTTPError:

                    try:

                        detail = response.json().get(
                            "detail",
                            "Invalid email or password."
                        )

                    except Exception:

                        detail = (
                            "Invalid email or password."
                        )

                    st.error(detail)

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to the FastAPI backend. "
                        "Make sure Uvicorn is running."
                    )

                except Exception as e:

                    st.error(
                        f"Login failed: {str(e)}"
                    )


    # ========================================================
    # REGISTER
    # ========================================================

    with tab2:

        st.subheader("Create Account")

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        if st.button(
            "Register",
            use_container_width=True
        ):

            if not register_email or not register_password:

                st.warning(
                    "Please enter an email and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_BASE_URL}/auth/register",
                        json={
                            "email": register_email,
                            "password": register_password
                        },
                        timeout=30
                    )

                    response.raise_for_status()

                    st.success(
                        "Account created successfully. "
                        "You can now login."
                    )

                except requests.exceptions.HTTPError:

                    try:

                        detail = response.json().get(
                            "detail",
                            "Registration failed."
                        )

                    except Exception:

                        detail = "Registration failed."

                    st.error(detail)

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to the FastAPI backend."
                    )

                except Exception as e:

                    st.error(
                        f"Registration failed: {str(e)}"
                    )

    st.stop()


# ============================================================
# LOAD USER DATA
# ============================================================

load_conversations()
load_documents()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("AI Developer Assistant")

    st.caption(
        "Multi-agent development assistant"
    )

    st.divider()


    # ========================================================
    # USER NAME
    # ========================================================

    display_name = get_display_name(
        st.session_state.user_email
    )

    st.write(
        f"**{display_name}**"
    )


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "+ New Chat",
        use_container_width=True
    ):

        if create_conversation():

            st.rerun()


    st.divider()


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    st.subheader("Chats")

    if st.session_state.conversations:

        for conversation in reversed(
            st.session_state.conversations
        ):

            title = conversation.get("title")

            if not title or title == "New Conversation":

                title = "New Chat"

            if len(title) > 38:

                title = (
                    title[:38].rstrip()
                    + "..."
                )

            is_active = (
                conversation["id"]
                == st.session_state.conversation_id
            )

            button_label = title

            if is_active:

                button_label = f"• {title}"

            if st.button(
                button_label,
                key=f"conversation_{conversation['id']}",
                use_container_width=True
            ):

                st.session_state.conversation_id = (
                    conversation["id"]
                )

                load_messages(
                    conversation["id"]
                )

                st.rerun()

    else:

        st.caption(
            "No chats yet."
        )


    st.divider()


    # ========================================================
    # DOCUMENTS
    # ========================================================

    st.subheader("Documents")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button(
            "Upload",
            use_container_width=True
        ):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{API_BASE_URL}/documents/upload",
                    headers=get_headers(),
                    files=files,
                    timeout=120
                )

                response.raise_for_status()

                data = response.json()

                st.success(
                    f"Uploaded successfully. "
                    f"{data['chunks']} chunks indexed."
                )

                load_documents()

                st.rerun()

            except requests.exceptions.HTTPError:

                try:

                    detail = response.json().get(
                        "detail",
                        "Document upload failed."
                    )

                except Exception:

                    detail = "Document upload failed."

                st.error(detail)

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI backend."
                )

            except Exception as e:

                st.error(
                    f"Upload failed: {str(e)}"
                )


    # ========================================================
    # DOCUMENT LIST
    # ========================================================

    if st.session_state.documents:

        for document in st.session_state.documents:

            st.write(
                f"**{document['filename']}**"
            )

            if st.button(
                "Delete",
                key=f"delete_document_{document['id']}",
                use_container_width=True
            ):

                try:

                    response = requests.delete(
                        f"{API_BASE_URL}/documents/"
                        f"{document['id']}",
                        headers=get_headers(),
                        timeout=30
                    )

                    response.raise_for_status()

                    st.success(
                        "Document deleted successfully."
                    )

                    load_documents()

                    st.rerun()

                except requests.exceptions.HTTPError:

                    try:

                        detail = response.json().get(
                            "detail",
                            "Could not delete document."
                        )

                    except Exception:

                        detail = (
                            "Could not delete document."
                        )

                    st.error(detail)

                except Exception as e:

                    st.error(
                        f"Delete failed: {str(e)}"
                    )


    st.divider()


    # ========================================================
    # AGENTS
    # ========================================================

    st.subheader("Agents")

    st.markdown("**Supervisor**")
    st.caption(
        "Routes requests to the appropriate agent."
    )

    st.markdown("**Coding Agent**")
    st.caption(
        "Handles coding, calculations and code analysis."
    )

    st.markdown("**Debug Agent**")
    st.caption(
        "Diagnoses programming errors and debugging issues."
    )

    st.markdown("**Research Agent**")
    st.caption(
        "Explains technical concepts and development topics."
    )


    st.divider()


    # ========================================================
    # TOOLS
    # ========================================================

    st.subheader("Available Tools")

    st.markdown("**Calculator**")
    st.caption(
        "Mathematical expression evaluation."
    )

    st.markdown("**Code Analyzer**")
    st.caption(
        "Python code analysis."
    )

    st.markdown("**Error Analyzer**")
    st.caption(
        "Python error diagnosis."
    )

    st.markdown("**Tech Info**")
    st.caption(
        "Technical information lookup."
    )


    st.divider()


    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.token = None
        st.session_state.user_email = None
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.conversations = []
        st.session_state.documents = []

        st.rerun()


# ============================================================
# MAKE SURE A CONVERSATION EXISTS
# ============================================================

if st.session_state.conversation_id is None:

    if create_conversation():

        st.rerun()

    else:

        st.error(
            "Could not create a conversation."
        )

        st.stop()


# ============================================================
# MAIN HEADER
# ============================================================

st.title("AI Developer Assistant")

st.caption(
    "Intelligent multi-agent assistant for coding, "
    "debugging, research and developer productivity."
)


# ============================================================
# WELCOME MESSAGE
# ============================================================

if not st.session_state.messages:

    st.info(
        "Ask a coding question, analyze a Python error, "
        "calculate an expression, review code, or ask "
        "questions about your uploaded documents."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a coding, debugging, or technical question..."
)


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

if user_input:

    # --------------------------------------------------------
    # Check if this is the first message
    # --------------------------------------------------------

    is_first_message = (
        len(st.session_state.messages) == 0
    )


    # --------------------------------------------------------
    # Create conversation title
    # --------------------------------------------------------

    if is_first_message:

        conversation_title = (
            user_input.strip()
        )

        if len(conversation_title) > 40:

            conversation_title = (
                conversation_title[:40].rstrip()
                + "..."
            )

        update_conversation_title(
            st.session_state.conversation_id,
            conversation_title
        )

        load_conversations()


    # --------------------------------------------------------
    # Add user message to UI
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):

        st.markdown(user_input)


    # --------------------------------------------------------
    # Send request to FastAPI
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Processing your request..."
        ):

            try:

                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    headers=get_headers(),
                    json={
                        "message": user_input,
                        "conversation_id": (
                            st.session_state.conversation_id
                        )
                    },
                    timeout=120
                )

                response.raise_for_status()

                data = response.json()

                final_response = data.get(
                    "response",
                    "I was unable to generate a response."
                )

                st.markdown(
                    final_response
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": final_response
                    }
                )


            # ------------------------------------------------
            # TIMEOUT
            # ------------------------------------------------

            except requests.exceptions.Timeout:

                st.error(
                    "The request took too long to complete. "
                    "Please try again."
                )


            # ------------------------------------------------
            # CONNECTION ERROR
            # ------------------------------------------------

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI backend. "
                    "Make sure Uvicorn is running."
                )


            # ------------------------------------------------
            # API ERROR
            # ------------------------------------------------

            except requests.exceptions.HTTPError:

                try:

                    error_detail = response.json().get(
                        "detail",
                        "Unknown API error."
                    )

                except Exception:

                    error_detail = response.text

                st.error(
                    f"API Error: {error_detail}"
                )


            # ------------------------------------------------
            # OTHER ERROR
            # ------------------------------------------------

            except Exception as e:

                st.error(
                    f"An unexpected error occurred: {str(e)}"
                )