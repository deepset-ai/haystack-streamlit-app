import streamlit as st

from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from haystack_integrations.components.retrievers.weaviate import WeaviateEmbeddingRetriever
from weaviate.embedded import EmbeddedOptions
from datasets import load_dataset
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.mistral import MistralChatGenerator
from haystack_integrations.components.embedders.mistral.document_embedder import MistralDocumentEmbedder
from haystack_integrations.components.embedders.mistral.text_embedder import MistralTextEmbedder
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.converters import TextFileToDocument, PyPDFToDocument, MarkdownToDocument
from haystack.components.routers import FileTypeRouter
from haystack.components.joiners import DocumentJoiner
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret
#U se this file to set up your Haystack pipeline and querying

@st.cache_resource(show_spinner=False)
def start_document_store():
    ## ℹ️ Choose your document store 
    document_store  = InMemoryDocumentStore()
    # document_store = WeaviateDocumentStore(embedded_options=EmbeddedOptions()) # Embedded version
    # document_store = WeaviateDocumentStore(url="rAnD0mD1g1t5.something.weaviate.cloud", auth_client_secret=AuthApiKey()) # Cloud
    # document_store = WeaviateDocumentStore(url="http://localhost:8080") # Self-hosted
    
    ## ℹ️ Option 1: Use components as standalone, index preprocessed files that are downloaded from Hugging Face
    # print("Document Store is initialized")
    # doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
    # print("Warming up the embedding model")
    # doc_embedder.warm_up()
    # print("Fetching documents")
    # dataset = load_dataset("bilgeyucel/seven-wonders", split="train") # no need for splitting, all docs are small enough
    # docs = [Document(content=doc["content"], meta=doc["meta"]) for doc in dataset]
    # print("Creating embeddings for documents")
    # docs_with_embeddings = doc_embedder.run(docs)
    # print("Indexing documents")
    # document_store.write_documents(docs_with_embeddings["documents"])
    
    
    ## ℹ️ Option 2: Alternatively, you can use a pipeline and index local files
    import nltk
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    file_router = FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/markdown"])
    text_converter = TextFileToDocument()
    pdf_converter = PyPDFToDocument() # requires 'pip install pypdf'
    markdown_converter = MarkdownToDocument()
    document_splitter = DocumentSplitter(split_by="word", split_length=150, split_overlap=10) # requires 'pip install nltk'
    # document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
    document_embedder = MistralDocumentEmbedder(model="mistral-embed", api_key=Secret.from_env_var("MISTRAL_API_KEY"))
    document_joiner = DocumentJoiner()
    document_writer = DocumentWriter(document_store=document_store)

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component(instance=file_router, name="file_router")
    indexing_pipeline.add_component(instance=text_converter, name="text_converter")
    indexing_pipeline.add_component(instance=pdf_converter, name="pdf_converter")
    indexing_pipeline.add_component(instance=markdown_converter, name="markdown_converter")
    indexing_pipeline.add_component(instance=document_joiner, name="document_joiner")
    indexing_pipeline.add_component(instance=document_splitter, name="document_splitter")    
    indexing_pipeline.add_component(instance=document_embedder, name="document_embedder")
    indexing_pipeline.add_component(instance=document_writer, name="document_writer")

    indexing_pipeline.connect("file_router.text/plain", "text_converter")
    indexing_pipeline.connect("file_router.application/pdf", "pdf_converter")
    indexing_pipeline.connect("file_router.text/markdown", "markdown_converter")
    indexing_pipeline.connect("markdown_converter", "document_joiner")
    indexing_pipeline.connect("text_converter", "document_joiner")
    indexing_pipeline.connect("pdf_converter", "document_joiner")
    indexing_pipeline.connect("document_joiner", "document_splitter")
    indexing_pipeline.connect("document_splitter", "document_embedder")
    indexing_pipeline.connect("document_embedder", "document_writer")

    indexing_pipeline.run(data={"file_router":{"sources":["files/example_file.txt", "files/example_file.md"]}})
    return document_store

# cached to make index and models load only at start
@st.cache_resource(show_spinner=False)
def start_haystack_pipeline(_document_store):
    template = [
        ChatMessage.from_user(
        """
        Given the following information, answer the question.

        Context:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}

        Question: {{question}}
        Answer:
        """
        )
    ]

    # text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
    text_embedder = MistralTextEmbedder(model="mistral-embed", api_key=Secret.from_env_var("MISTRAL_API_KEY"))
    retriever = InMemoryEmbeddingRetriever(_document_store)
    # retriever = WeaviateEmbeddingRetriever(document_store=_document_store)
    prompt_builder = ChatPromptBuilder(template=template)
    chat_generator = MistralChatGenerator(model="mistral-large-latest", api_key=Secret.from_env_var("MISTRAL_API_KEY")) 
    
    basic_rag_pipeline = Pipeline()
    
    basic_rag_pipeline.add_component("text_embedder", text_embedder)
    basic_rag_pipeline.add_component("retriever", retriever)
    basic_rag_pipeline.add_component("prompt_builder", prompt_builder)
    basic_rag_pipeline.add_component("chat_generator", chat_generator)
    
    basic_rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    basic_rag_pipeline.connect("retriever", "prompt_builder")
    basic_rag_pipeline.connect("prompt_builder.prompt", "chat_generator.messages")
    return basic_rag_pipeline

@st.cache_data(show_spinner=True)
def query(_pipeline, question):
    print("Pipeline will run with query:", question)
    results = _pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}}, include_outputs_from={"chat_generator"})
    return results