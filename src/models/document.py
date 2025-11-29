from dataclasses import dataclass
from typing import Dict

@dataclass
class Document:
    """Модель документа для индексации"""
    id: str
    text: str
    term_count: int = 0
    
    def __post_init__(self):
        self.term_count = len(self.text.split())

@dataclass 
class SearchResult:
    """Результат поиска"""
    document: Document
    score: float
    snippet: str = ""