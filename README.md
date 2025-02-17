👨‍💻 Contributors
Abenanth ; Contributions welcome! Open a PR or issue. 😊
⭐ Support
If you like this project, give it a star! ⭐


# 🇨🇦 Canadian History Chatbot

An interactive chatbot powered by LangChain, Pinecone, OpenAI, and Streamlit for answering questions about Canadian history.

![Chatbot Screenshot](https://via.placeholder.com/800x400?text=Chatbot+UI+Preview)

---

## 📌 Features
- 🔐 **User Authentication (Login/Register)**
- 💬 **Conversational Chatbot with LangChain**
- 📚 **Retrieval-Augmented Generation (RAG) using Pinecone**
- 🧠 **Long-Term Memory with SQLite3**
- ✨ **Modern UI with Streamlit**
- 🎯 **Real-Time User Feedback System**
- ⚡ **Efficient Search & Response Handling**
- 🔄 **Session Management for Seamless Navigation**

---

## 🏗 Tech Stack
| Technology    | Purpose |
|--------------|---------|
| **Streamlit**  | UI & Web Framework |
| **OpenAI API** | GPT-powered response generation |
| **LangChain**  | Conversational AI framework |
| **Pinecone**   | Vector database for document retrieval |
| **SQLite3**    | Database for chat history & authentication |
| **bcrypt**     | Secure password hashing |
| **Tavily API** | Enhanced web search |

---

## 🚀 Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/chatbot_ca_history.git
cd chatbot_ca_history
pip install -r requirements.txt
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
TAVILY_API_KEY=your_tavily_key
streamlit run app.py
```
--------------------------------------------------------------------------------

🛠 Project Structure
│── data/                          # Data storage (if needed)
│── models/                        # Model-related scripts
│── static/                        # Static files (images, icons)
│── utils/                         # Utility functions (DB, authentication)
│── app.py                          # Main Streamlit chatbot application
│── database.py                     # SQLite3 Database operations
│── setup_db.py                     # Database initialization script
│── requirements.txt                 # Dependencies
│── README.md                        # Project Documentation

-------------------------------------------------------------------------------

🔑 Core Functionalities
**1️⃣ User Authentication (Login & Registration)**
Uses bcrypt to securely store passwords.
SQLite3 stores user credentials.
Only logged-in users can access the chatbot.
**2️⃣ Conversational Chatbot (LangChain & OpenAI)**
Accepts user queries about Canadian history.
Uses LangChain and GPT to generate responses.
**3️⃣ Pinecone for Document Retrieval (RAG)**
Converts user queries into embeddings.
Searches for relevant historical documents.
Uses similarity search for accurate results.
**4️⃣ SQLite3 for Long-Term Memory**
Stores chat history per user.
Allows users to retrieve past conversations.
**5️⃣ User Feedback System**
Users can rate chatbot responses as 👍 Helpful or 👎 Not Helpful.
Stores feedback in the database for continuous improvement.
**6️⃣ Tavily API for Web Search**
Enhances chatbot knowledge with real-time information.

---------------------------------------------------------------------------------

📚 Future Improvements
✅ Improve response quality with better prompt engineering.
✅ Optimize vector search for faster results.
✅ Implement Admin Dashboard to analyze chatbot performance.
✅ Add voice input for better accessibility.

----------------------------------------------------------------------------------

📜 License
This project is licensed under the MIT License.

----------------------------------------------------------------------------------

📩 Contact
For queries, reach out via [LinkedIn](https://www.linkedin.com/in/kalyanaabenanthg/) or email 📧 kalyanaa@ualberta.ca.
