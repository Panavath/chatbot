from enum import Enum

class FileType(str, Enum):
    PDF     = 'application/pdf'
    TXT     = 'text/plain'
    DOCX    = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    CSV     = 'text/csv'
