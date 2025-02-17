from openai import OpenAI
import os
from PyPDF2 import PdfReader
import tiktoken
from pinecone import Pinecone, ServerlessSpec

pinecone_key = os.environ.get("pinecone_key")
# Connection to Pinecone with key
pc= Pinecone(api_key=pinecone_key)
api_key=os.getenv("openai_api")
client = OpenAI(api_key=api_key)
tokenizer = tiktoken.get_encoding("cl100k_base")  # Used for `text-embedding-3-small`

# Creating Index in pinecode to store embeddings
try:
    pc.create_index(name="history-index",dimension=1536,deletion_protection="enabled",spec=ServerlessSpec(cloud='aws',region='us-east-1'))
    # connecting to the index
    index = pc.Index("history-index")
except Exception as e:
    # since index is already created accessing it
    index = pc.Index("history-index")


# Function to count tokens in a string
def count_tokens(text):
    return len(tokenizer.encode(text))

# Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:  # Avoid NoneType errors
            text += extracted + "\n"
    return text.strip()

# Split text into 3000-word chunks
def chunk_text(text, max_words=100):
    words = text.split()  # Split by words
    chunks = [" ".join(words[i: i + max_words]) for i in range(0, len(words), max_words)]
    return chunks

# Load and chunk a sample PDF
pdf_path = "C:\\Users\\kalya\\Desktop\\Desktop\\Law_Books\\Canadian_History.pdf"
full_text = extract_text_from_pdf(pdf_path)
chunks = chunk_text(full_text)

print(f"Total Chunks Created: {len(chunks)}")

# Function to generate embeddings and store in Pinecone
def store_embeddings(chunks):
    for i, chunk in enumerate(chunks):
        response = client.embeddings.create(
            input=chunk,
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        index.upsert([(f"chunk-{i}", embedding, {"text": chunk})])  # Store with metadata

# Store PDF chunks in Pinecone
store_embeddings(chunks)
print("PDF Embeddings Stored Successfully!")

# Function to query Pinecone
def query_pinecone(query_text, top_k=1):
    # Convert query text into an embedding
    response = client.embeddings.create(
        input=query_text,
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding

    # Perform similarity search in Pinecone
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    # Display results
    for match in results["matches"]:
        print(f"Score: {match['score']}\nText: {match['metadata']['text']}\n")

# Example query
query_text = input("Enter the quesion : \n")
query_pinecone(query_text)







