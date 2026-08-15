import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from factories import get_embeddings, get_llm

load_dotenv()

DB_PATH = "./chroma_db"

# Fallback defaults used when the corresponding .env variables are empty.
DEFAULT_WELCOME_MESSAGE = "🚀 Welcome to the RAG Bot! (Type 'exit' to quit)"
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the following context to answer the question "
    "as precisely as possible. If you don't know the answer based on the context, "
    "say so clearly.\n\n"
    "Context:\n{context}"
)


def _load_system_prompt() -> str:
    """Loads SYSTEM_PROMPT from .env and ensures it exposes the {context} placeholder."""
    system_prompt = os.getenv("SYSTEM_PROMPT") or DEFAULT_SYSTEM_PROMPT
    # Escape literal braces (e.g. JSON examples in a custom prompt) so
    # ChatPromptTemplate doesn't treat them as template variables,
    # then restore the {context} placeholder.
    system_prompt = system_prompt.replace("{", "{{").replace("}", "}}")
    system_prompt = system_prompt.replace("{{context}}", "{context}")
    if "{context}" not in system_prompt:
        # Append the context block automatically so the retrieval chain can inject documents.
        system_prompt = f"{system_prompt}\n\nContext:\n{{context}}"
    return system_prompt


def main():
    # 1. Load configuration from environment.
    welcome_message = os.getenv("WELCOME_MESSAGE") or DEFAULT_WELCOME_MESSAGE
    default_question = os.getenv("DEFAULT_QUESTION", "")
    system_prompt = _load_system_prompt()

    # 2. Model configuration.
    embedding_model = get_embeddings()
    llm = get_llm()

    # 3. Load the vector store.
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 4. Build the prompt template from the .env-provided system prompt.
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 5. Build the RAG chain.
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    print(f"\n{welcome_message}")
    if default_question:
        print(f"💡 Example question: {default_question}")

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == "exit":
            break

        # Fall back to the .env-provided default question when the user submits empty input.
        question = user_input or default_question
        if not question:
            continue

        response = rag_chain.invoke({"input": question})
        print(f"\n🤖 Answer:\n{response['answer']}")


if __name__ == "__main__":
    main()
