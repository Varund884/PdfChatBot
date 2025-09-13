# Importing the libraries.
# Using Streamlit for the Frontend UI.
import streamlit as st
# Using cohere for the LLM.
import cohere
import os
# Storing the api key in the .env file.
from dotenv import load_dotenv
# Using fitz to read through the PDFs.
import fitz 

# Configurating the webpage with title.
st.set_page_config(page_title="📄 Talk to PDF AI", page_icon="🤖", layout="centered")
# Alligning the title in the middle.
st.markdown(
    "<h1 style='text-align: center; color: #ffffff;'>📄 Talk to PDF AI Chatbot</h1>",
    unsafe_allow_html=True
)

# Calling the Cohere LLM using the API key.
co = cohere.Client(os.getenv("COHERE_API_KEY"))
# Human Input emoji.
USER_EMOJI = "👨🏻‍💼"
# Reply emoji.
ASSISTANT_EMOJI = "👉"

# Storing messages, chat and Uploaded pdf into the memory.
if "messages" not in st.session_state:
    st.session_state.messages = []
# Pdf Text
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
# Upload key
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Sidebar controls.
with st.sidebar:
    # Heading
    st.markdown(
        """
        <div style="text-align: center;">
            <h2>⚙️ Controls</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Subheading
    st.markdown(
        """
        <div style="text-align: center;">
            📂 Upload a PDF
        </div>
        """,
        unsafe_allow_html=True
    )
    # User upload the file here.
    uploaded_file = st.file_uploader("", type=["pdf"], key=st.session_state.uploader_key)

    # Lets start a new chat by clicking the button.
    if st.button("🆕 Start New Chat", use_container_width=True):
        st.session_state.messages = []        
        st.session_state.pdf_text = ""
        # Incrementing the file upload for fresh new chat with again asking fot the file upload.    
        st.session_state.uploader_key += 1
        st.rerun()

    # Guides
    st.markdown(
        """
        ### 📌 How to use this app ?
        1. Click **🆕 Start New Chat** to reset the conversation.
        2. Upload a PDF using the **📂 Upload a PDF** button.
        3. Wait a few seconds while the PDF is processed.
        4. Ask any questions about the PDF in the chat input.
        5. The assistant will respond using the PDF content.
        6. To start over, simply click **🆕 Start New Chat** again.
        """
    )

# Upload PDF here.
if uploaded_file is not None and st.session_state.pdf_text == "":
    # Extracting the text from the pdf.
    with st.spinner("Extracting text from PDF..."):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        st.session_state.pdf_text = text
    # Displaying the success message.
    st.success("✅ PDF uploaded and processed successfully!")

# Displaying the messages.
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_EMOJI):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=ASSISTANT_EMOJI):
            st.markdown(message["content"])

# User prompts.
if prompt := st.chat_input("Ask me anything about the PDF!"):
    if not st.session_state.pdf_text:
        # Warning message if no pdf found.
        st.warning("⚠️ Please upload a PDF first.")
    else:
        # Adding user messages here.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_EMOJI):
            st.markdown(prompt)

        # Prepareing the conversation history for better followups.
        conversation_history = ""
        for msg in st.session_state.messages:
            speaker = "User" if msg["role"] == "user" else "Assistant"
            conversation_history += f"{speaker}: {msg['content']}\n"

        # Bot Loading messages.
        with st.spinner("🙏 Please wait the bot is 🤔 Thinking..."):
            # Prompt Engineering starts here.
            response = co.chat(
                # Using basic cohere model.
                model="command-r",
                # Promting the llm for better results.
                message=(
                "You are an AI assistant that can do two things:\n"
                "1. If the user greets you (hi, hello, bye, thanks, etc.), respond naturally as a friendly chatbot who can respond based on the pdf uploaded.\n"
                "2. If the user asks about the PDF, ONLY use the PDF content provided below to answer and answer in short summarised way with bullet points when needed.\n"
                "3. If the question is unrelated to the PDF, politely say you can only answer based on the PDF.\n\n"
                f"Here is the PDF content:\n\n{st.session_state.pdf_text}\n\n"
                f"Conversation so far:\n{conversation_history}\n\n"
                f"User's question: {prompt}"
            ),
                # Setting the medium model response parameter.            
                max_tokens=300,
                # Setting the safer creativity responses.
                temperature=0.3
            )

        # LLM responsing the text.
        assistant_reply = response.text
        # Assistant displaying the output.
        with st.chat_message("assistant", avatar=ASSISTANT_EMOJI):
            st.markdown(assistant_reply)
        # Storing User and Bot variables.
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
