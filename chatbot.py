import streamlit as st
from openai import OpenAI
from pinecone import Pinecone
import os

# Initialize OpenAI client
api_key=os.getenv("openai_api")
client = OpenAI(api_key=api_key)

# Initialize Pinecone
pinecone_key = os.environ.get("pinecone_key")
pc= Pinecone(api_key=pinecone_key)
index = pc.Index("history-index")

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

def generate_answer(query):
    """Generate an answer using OpenAI's GPT model with retrieved context."""
    retrieved_texts = query_pinecone(query)
    context = "\n\n".join(retrieved_texts)
    
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        max_tokens=150,
        messages=[
            {"role": "system", "content": "You are a knowledgeable historian specializing in Canadian history."},
            {"role": "user", "content": f"Based on the following information, answer the question:\n\n{context}\n\nQuestion: {query}"}
        ]
    )
    
    return completion.choices[0].message.content

# Function to limit input to 20 words
def limit_input(user_input):
    # Split the input into words and limit to 20 words
    words = user_input.split()
    if len(words) > 20:
        st.warning("Your input exceeds 20 words. It has been truncated.")
        return ' '.join(words[:20])  # Truncate to 20 words
    return user_input


# Streamlit UI
st.set_page_config(page_title="Canadian History Chatbot")
st.title("🇨🇦 Canadian History Chatbot")
st.write("Ask a question about Canadian history and get an AI-powered response!")

# User input
# limit user input to 20 words
user_query = st.text_input("Ask me anything about Canadian history:")
# Apply the limit to the input
if user_query:
    user_query = limit_input(user_query)
    response = generate_answer(user_query)
    st.write("**Chatbot:**", response)

