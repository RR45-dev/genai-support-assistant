import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ragadmin:ragadmin@localhost:5432/support_kb")

# Azure OpenAI (used for both embeddings-fallback-free generation and the
# chat completion step). If these are unset, rag.py falls back to a purely
# extractive answer built from the top retrieved chunks, so the whole stack
# is runnable with zero API keys for local development/demo purposes.
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")

# Optional: source documents can be pulled from S3 instead of the local
# ./docs folder (useful when this runs on Azure but docs are managed in an
# existing S3-based content pipeline).
S3_BUCKET = os.getenv("DOCS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384
TOP_K = int(os.getenv("RAG_TOP_K", "4"))

SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL")
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN")
