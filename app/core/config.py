from typing import Dict

from pydantic_settings import BaseSettings
from decouple import config

from app.core.enum.file_enum import FileType

class Settings(BaseSettings):

    API_V1_STR              : str   = "/api/v1"

    API_NAME                : str   = "LLM-Agent"
    API_VERSION             : str   = "1.0"
    MODEL_NAME              : str   = config('MODEL_NAME')

    CHROMADB_HOST           : str   = config('CHROMADB_HOST'      , cast=str)
    CHROMADB_PORT           : int   = config('CHROMADB_PORT'      , cast=int)

    DB_USER                 : str   = config('DB_USER'          , cast=str)
    DB_PASS                 : str   = config('DB_PASS'          , cast=str)
    DB_NAME                 : str   = config('DB_NAME'          , cast=str)
    DB_HOST                 : str   = config('DB_HOST'          , cast=str)

    DB_PORT                 : int   = config('DB_PORT'          , cast=int)

    OPENAI_API_KEY          : str   = config('OPENAI_API_KEY'   , cast=str)

    GOOGLE_GENAI_API_KEY    : str   = config('GOOGLE_GENAI_API_KEY', cast=str)

    # Search ap[i key
    TAVILY_API_KEY          : str   = config('TAVILY_API_KEY'   , cast=str)


    SUPPORTED_FORMATS       : Dict[str, str] = {
                                FileType.PDF: '.pdf'
                                , FileType.TXT: '.txt'
                                , FileType.DOCX: '.docx'
                                , FileType.CSV: '.csv'
                            }


settings    = Settings()

def get_file_extension(file_type: str) -> str:
    return settings.SUPPORTED_FORMATS.get(file_type, '')

def is_supported_file_type(file_type: str) -> bool:
    return file_type in settings.SUPPORTED_FORMATS

