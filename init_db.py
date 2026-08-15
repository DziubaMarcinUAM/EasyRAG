import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from factories import get_embeddings

DOCS_PATH = "./docs"
DB_PATH = "./chroma_db"

def build_database():
    print("Starting to build knowledge base...")
    
    # 1. Load documents
    # Explicit utf-8 so native Windows runs don't fall back to the system codepage.
    loader = DirectoryLoader(
        DOCS_PATH,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    
    if not documents:
        print(f"No documents found in {DOCS_PATH}. Stopping.")
        return

    # 2. Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 3. Save to Chroma DB
    embedding_model = get_embeddings()
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)

    # Drop any previously indexed chunks so re-running init doesn't duplicate documents.
    vectorstore.reset_collection()


    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vectorstore.add_documents(batch)
    print("Vector database saved successfully!")

if __name__ == "__main__":
    build_database()