import os
from dotenv import load_dotenv

load_dotenv()


def get_embeddings():
    """Returns the embedding model based on .env configuration.

    Supported providers: local, anthropic, azure, openai, vertex.
    """
    provider = os.getenv("EMBEDDINGS_PROVIDER", "local").lower()

    if provider == "local":
        # "or" fallback so that empty values in .env don't override the default.
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL") or "all-MiniLM-L6-v2"
        print(f"⚙️ Loading Embeddings: Local HuggingFace model ({model_name})")
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=model_name)

    elif provider == "openai":
        model_name = os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-small"
        print(f"⚙️ Loading Embeddings: OpenAI ({model_name})")
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model_name)

    elif provider == "azure":
        # AZURE_EMBEDDING_MODEL is treated as the Azure deployment name for the embedding model.
        deployment = os.getenv("AZURE_EMBEDDING_MODEL")
        endpoint = os.getenv("AZURE_AI_ENDPOINT")
        api_key = os.getenv("AZURE_AI_API_KEY")
        api_version = os.getenv("AZURE_API_VERSION") or "2024-02-15-preview"
        print(f"⚙️ Loading Embeddings: Azure OpenAI (Deployment: {deployment})")
        from langchain_openai import AzureOpenAIEmbeddings
        return AzureOpenAIEmbeddings(
            azure_deployment=deployment,
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

    elif provider == "anthropic":
        # Anthropic does not provide a native embeddings API
        # The official recommendation is Voyage AI
        # ANTHROPIC_EMBEDDING_MODEL is expected to hold a Voyage AI model id (e.g. "voyage-3")
        model_name = os.getenv("ANTHROPIC_EMBEDDING_MODEL") or "voyage-3"
        print(
            f"⚙️ Loading Embeddings: Voyage AI ({model_name}) "
            f"— Anthropic's recommended embedding provider"
        )
        from langchain_voyageai import VoyageAIEmbeddings
        return VoyageAIEmbeddings(model=model_name)

    elif provider == "vertex":
        # Vertex requires the GCP project id and location.
        model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-multilingual-embedding-002")
        project = os.getenv("VERTEX_AI_PROJECT_ID") or None
        location = os.getenv("VERTEX_AI_LOCATION", "global")
        print(f"⚙️ Loading Embeddings: Google Vertex AI ({model_name})")
        from langchain_google_vertexai import VertexAIEmbeddings
        return VertexAIEmbeddings(
            model_name=model_name,
            project=project,
            location=location,
        )

    raise ValueError(f"Unknown embeddings provider: {provider}")


def get_llm():
    """Returns the main language model based on .env configuration.

    Supported providers: anthropic, openai, azure, vertex.
    """
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

    if provider == "anthropic":
        # claude-3-5-sonnet was retired (Oct 2025); claude-sonnet-5 is the current Sonnet tier.
        model_name = os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-5"
        print(f"🧠 Loading LLM: Anthropic Claude ({model_name})")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model_name, temperature=0)

    elif provider == "openai":
        model_name = os.getenv("OPENAI_MODEL") or "gpt-4o"
        print(f"🧠 Loading LLM: OpenAI ({model_name})")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, temperature=0)

    elif provider == "azure":
        # AZURE_MODEL is treated as the Azure deployment name for the chat model.
        deployment = os.getenv("AZURE_MODEL")
        endpoint = os.getenv("AZURE_AI_ENDPOINT")
        api_key = os.getenv("AZURE_AI_API_KEY")
        api_version = os.getenv("AZURE_API_VERSION") or "2024-02-15-preview"
        print(f"🧠 Loading LLM: Azure AI Foundry (Deployment: {deployment})")
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            azure_deployment=deployment,
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            temperature=0,
        )

    elif provider == "vertex":
        model_name = os.getenv("VERTEX_MODEL", "gemini-1.5-pro-001")
        project = os.getenv("VERTEX_AI_PROJECT_ID") or None
        location = os.getenv("VERTEX_AI_LOCATION", "europe-west1")
        print(f"🧠 Loading LLM: Google Vertex AI ({model_name} in {location})")
        from langchain_google_vertexai import ChatVertexAI
        return ChatVertexAI(
            model_name=model_name,
            project=project,
            location=location,
            temperature=0,
        )

    raise ValueError(f"Unknown LLM provider: {provider}")
