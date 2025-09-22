import logging
import os
from bs4 import BeautifulSoup as Soup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

VSTORE_DIR = "../data/vector_store"

def setup_vector_store(logger: Optional[logging.Logger] = None):
    """Setup or load the vector store (FAISS)."""
    if logger is None:
        logger = logging.getLogger(__name__)
    if not os.path.exists("data"):
        os.makedirs("data")
    vector_store_dir = VSTORE_DIR
    if os.path.exists(vector_store_dir):
        # Load the vector store from disk
        logger.info("Loading vector store from disk...")
        vector_store = FAISS.load_local(
            vector_store_dir,
            OpenAIEmbeddings(),
            allow_dangerous_deserialization=True,
        )
    else:
        logger.info("Creating new vector store...")
        # Load SQL documentation from W3Schools
        url = "https://www.w3schools.com/sql/"
        loader = RecursiveUrlLoader(url=url, max_depth=2, extractor=lambda x: Soup(x, "html.parser").text)
        docs = loader.load()
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )
        documents = []
        for doc in docs:
            splits = text_splitter.split_text(doc.page_content)
            for i, split in enumerate(splits):
                documents.append(
                    {
                        "content": split,
                        "metadata": {"source": doc.metadata.get("source", ""), "chunk": i},
                    }
                )
        # Compute embeddings and create vector store
        embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        vector_store = FAISS.from_texts(
            [doc["content"] for doc in documents],
            embedding_model,
            metadatas=[doc["metadata"] for doc in documents],
        )
        # Save the vector store to disk
        vector_store.save_local(vector_store_dir)
        logger.info("Vector store created and saved to disk.")
    return vector_store
