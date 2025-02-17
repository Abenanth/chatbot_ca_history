import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pinecone import Pinecone
import os
import hashlib
import sqlite3
from tavily import TavilyClient
from openai import OpenAI
# from streamlit_extras.app_logo import add_logo

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc= Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("history-index")

# Initialize Tavily Client
tavily_key = os.getenv("tavily_key")
tavily_client = TavilyClient(api_key=tavily_key)
DB_PATH = "chatbot_memory.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            user_message TEXT,
            bot_response TEXT,
            feedback TEXT DEFAULT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


# Password Hashing Function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User Authentication
def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == hash_password(password):
        return True
    return False

# Register New User
def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Save Chat History
def save_chat_history(username, user_message, bot_response, feedback=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (username, user_message, bot_response, feedback) VALUES (?, ?, ?, ?)",
                   (username, user_message, bot_response, feedback))
    conn.commit()
    conn.close()

# Retrieve Chat History
def get_chat_history(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, bot_response, feedback FROM chat_history WHERE username = ? ORDER BY timestamp DESC LIMIT 10", (username,))
    history = cursor.fetchall()
    conn.close()
    return history

# Retrieve Context from Pinecone
def query_pinecone(query, top_k=5):
    """Retrieve relevant history text from Pinecone based on user query."""
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding

    search_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    retrieved_texts = [match["metadata"]["text"] for match in search_results["matches"]]
    return retrieved_texts

# Retrieve Web Data from Tavily
def query_tavily(query):
    try:
        search_result = tavily_client.search(query=query,search_depth="basic",max_results=2)
        return "\n\n".join([result["content"] for result in search_result["results"]])
    except Exception as e:
        return f"Tavily Error: {str(e)}"


# LangChain LLM to generate answers
def generate_answer_with_langchain(query):
    """Generate an answer using LangChain with OpenAI's GPT model and retrieved context."""
    
    # Retrieve context from Pinecone
    retrieved_texts = query_pinecone(query)
    context = "\n\n".join(retrieved_texts)
    
    # Retrieve additional web data from Tavily
    web_data = query_tavily(query)

    # Create a prompt using LangChain
    prompt_template = PromptTemplate(
        input_variables=["query", "context", "web_data"],
        template="""
                You are a knowledgeable historian and AI assistant specializing in Canadian history.
                Your goal is to provide **factually accurate**, **detailed**, and **well-structured** responses.

                ---
                **User Question:** {query}
                
                **Retrieved Context from Historical Records & Database:** 
                {context}

                **Additional Web Data (Real-Time Information):** 
                {web_data}
                
                ---
                🔹 **Response Guidelines**:
                1️⃣ Prioritize retrieved context from history records.  
                2️⃣ If web data is available, cross-check and **enhance** the response.  
                3️⃣ Provide a **clear summary**, followed by a **detailed explanation**.  
                4️⃣ **If data is missing**, acknowledge the gap and suggest alternative sources.  

                ---
                **Answer Format**:
                - **Summary** (2-3 sentences)  
                - **Detailed Explanation** (historical insights, examples)  
                - **References** (database, Pinecone, or Tavily sources)
                
                ---
                Now, provide a well-structured answer based on the available data.
                """
            )

    # Use LangChain to run the LLM with the created prompt
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4-turbo", max_tokens=100)
    chain = prompt_template | llm
    
    # Run the chain and return response
    response = chain.invoke({"query": query, "context": context, "web_data": web_data})
    return response.content

# Function to limit input to 20 words
def limit_input(user_input):
    words = user_input.split()
    if len(words) > 20:
        st.warning("Your input exceeds 20 words. It has been truncated.")
        return ' '.join(words[:20])  # Truncate to 20 words
    return user_input

# 🏠 **Streamlit UI Configuration**
st.set_page_config(page_title="🇨🇦 Canadian History Chatbot", page_icon="📖", layout="wide")

# 🎨 **Custom Styling**
st.markdown("""
    <style>
        body {font-family: 'Arial', sans-serif;}
        .title {color: #1F618D; text-align: center; font-size: 36px; font-weight: bold;}
        .subheader {color: #2874A6; text-align: center; font-size: 24px; font-weight: bold;}
        .stButton>button {border-radius: 10px; font-size: 18px; padding: 8px 16px; background-color: #1F618D; color: white;}
        .stTextInput>div>div>input {border-radius: 10px; font-size: 16px; padding: 6px;}
        .stRadio>label {color: #1F618D; font-weight: bold;}
        .chat-box {background-color: #EAEDED; padding: 15px; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# 🔄 **Session State for User Authentication**
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 🌟 **Sidebar Navigation**
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Canada_%28Pantone%29.svg/2560px-Flag_of_Canada_%28Pantone%29.svg.png", width=200)
    st.subheader("📖 Canadian History Chatbot")
    st.write("Ask anything about Canada's past, from indigenous history to modern times.")
    st.markdown("---")  # Divider
    # 💡 Developer Info
    st.subheader("👨‍💻 Developed by:")
    st.write("**Kalyana Abenanth Gurunathan**")
    st.write("🖥️ ML Engineer")

    # 🌐 Social Links with Icons
    st.markdown(
        """
        🔗 [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kalyanaabenanthg/)  
        💻 [![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/Abenanth)  
        📧 [Email](mailto:kalyanaa@ualberta.ca)
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")  # Divider


    if st.session_state["logged_in"]:
        st.write(f"👤 Logged in as: **{st.session_state['username']}**")
        if st.button("🔓 Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state.pop("username", None)
            st.success("Logged out successfully!")
            st.rerun()

# 🔐 **Login / Register UI**
if not st.session_state["logged_in"]:
    st.markdown("<h1 class='title'>🔐 Login or Register</h1>", unsafe_allow_html=True)
    
    option = st.radio("Choose an option:", ["Login", "Register"], horizontal=True)
    username = st.text_input("👤 Username:")
    password = st.text_input("🔑 Password:", type="password")

    col1, col2 = st.columns(2)
    
    with col1:
        if option == "Login" and st.button("✅ Login"):
            if authenticate_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"🎉 Welcome back, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try again.")

    with col2:
        if option == "Register" and st.button("📝 Register"):
            if register_user(username, password):
                st.success("🎊 Registration successful! Please log in.")
            else:
                st.error("⚠️ Username already exists.")

# 🤖 **Chatbot UI**
if st.session_state["logged_in"]:
    st.markdown(f"<h1 class='title'>💬 Welcome, {st.session_state['username']}!</h1>", unsafe_allow_html=True)
    
    # **User Query with Button**
    user_query = st.text_input("🔎 Ask a question about Canadian history:")
    query_button = st.button("📩 Send Question", use_container_width=True)

    if query_button and user_query:
        response = generate_answer_with_langchain(user_query)

        # 💾 Save chat history
        save_chat_history(st.session_state["username"], user_query, response)

        # 💬 Display chat response
        with st.container():
            st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
            st.write(f"👤 **You:** {user_query}")
            st.write(f"🤖 **Chatbot:** {response}")
            st.markdown("</div>", unsafe_allow_html=True)

        # ⭐ **Feedback System**
        feedback = st.radio("Was this answer helpful?", ["👍 Yes", "👎 No"], index=None)
        if feedback:
            save_chat_history(st.session_state["username"], user_query, response, feedback)
            st.success("✅ Thanks for your feedback! 😊")

    # 📜 **Show Past Chat History**
    if st.button("📂 Show Chat History", use_container_width=True):
        history = get_chat_history(st.session_state["username"])
        st.markdown("<h3 class='subheader'>📜 Your Chat History</h3>", unsafe_allow_html=True)

        if history:
            for user_message, bot_response, feedback in history:
                with st.container():
                    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
                    st.write(f"👤 **You:** {user_message}")
                    st.write(f"🤖 **Bot:** {bot_response}")
                    if feedback:
                        st.write(f"⭐ **Feedback:** {feedback}")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No chat history found.")
