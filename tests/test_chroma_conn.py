import os
import chromadb

from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

CHROMADB_HOST   = os.getenv("CHROMADB_HOST")
CHROMADB_PORT   = os.getenv("CHROMADB_PORT")
CHROMADB_USER   = os.getenv("CHROMADB_USER")
CHROMADB_PASS   = os.getenv("CHROMADB_PASS")
CHROMA_SERVER_AUTHN_CREDENTIALS = os.getenv("CHROMA_SERVER_AUTHN_CREDENTIALS")
CHROMA_SERVER_AUTHN_PROVIDER    = os.getenv("CHROMA_SERVER_AUTHN_PROVIDER")


client  = chromadb.HttpClient(
    host    = CHROMADB_HOST
    , port  = CHROMADB_PORT
)

collection = client.create_collection(name="collection_v1sd")
