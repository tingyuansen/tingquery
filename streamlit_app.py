import pysqlite3 
import sys 
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import pickle
import chromadb
import os
import openai
import numpy as np

# Load the precomputed data
def load_data(doc_file, emb_file):
    with open(doc_file, 'rb') as file:
        documents = pickle.load(file)
    embeddings = np.load("embeddings.npy")
    return documents, embeddings

def create_chroma_collection(documents, embeddings, collection_name="my_embeddings_collection"):
    chroma_client = chromadb.Client()
    try:
        # Try to get an existing collection
        chroma_collection = chroma_client.get_collection(collection_name)
    except Exception:
        # If it does not exist, create a new one
        chroma_collection = chroma_client.create_collection(collection_name)
        ids = [str(i) for i in range(len(documents))]
        chroma_collection.add(ids=ids, documents=documents, embeddings=embeddings)
    return chroma_collection

# Load data and setup ChromaDB
documents, embeddings = load_data("documents.pkl", "embeddings.npy")
chroma_collection = create_chroma_collection(documents, embeddings)

# Streamlit application setup
st.set_page_config(page_title="🌟 Have questions about our research?", layout="wide")
st.markdown("### 🌟 Have questions about our research?", unsafe_allow_html=True)

# Introduction to the application
st.write("""
In this application, we've ingested all the papers published by our research group into an AI-powered tool to perform Retrieval-Augmented Generation (RAG) and summarization. This enables you to ask questions and get insights based on our research output.

Due to privacy and security concerns, you need to provide your own OpenAI API key to activate the AI features. Please obtain an API key from [OpenAI's website](https://openai.com/) and enter it below to get started.
""")

st.markdown("")

# Display example questions as buttons
example_questions = [
    "What is thick disk?",
    "What is normalizing flow?",
    "What is parity violation?"
]

st.write("**Example questions you can ask:**")
col1, col2, col3 = st.columns(3)

# Initialize or update session state
if 'query_text' not in st.session_state:
    st.session_state.query_text = ''

with col1:
    if st.button(example_questions[0]):
        st.session_state.query_text = example_questions[0]
with col2:
    if st.button(example_questions[1]):
        st.session_state.query_text = example_questions[1]
with col3:
    if st.button(example_questions[2]):
        st.session_state.query_text = example_questions[2]

# Input field that updates based on button clicks
query_input = st.text_input('Enter your question:', value=st.session_state.query_text, placeholder='')

# OpenAI API Key input
openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if openai_api_key:  # Ensure the API key is used immediately after being input
    os.environ['OPENAI_API_KEY'] = openai_api_key
    openai.api_key = openai_api_key
    openai_client = openai.OpenAI()

if st.button('Submit') and query_input:
    try:
        with st.spinner('Searching documents...'):
            results = chroma_collection.query(query_texts=[query_input], n_results=5)
            retrieved_documents = results['documents'][0]
    
        with st.spinner('Generating response...'):
            information = "\n\n".join(retrieved_documents)
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful expert. Answer the user's question using the information provided."
                },
                {"role": "user", "content": f"Question: {query_input}. \nInformation: {information}"}
            ]
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            content = response.choices[0].message.content

        st.subheader("Response:")
        st.write(content)

    except:
        st.error("Invalid OpenAI API key. Please enter a valid API key.")
        
    
