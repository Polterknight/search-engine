import json
from typing import Dict, List
from ..models.document import Document

class InvertedIndex:
    """Инвертированный индекс для быстрого поиска"""
    
    def __init__(self):
        self.terms: Dict[str, Dict[str, int]] = {}  # term -> {doc_id: tf}
        self.documents: Dict[str, Document] = {}
        self.total_docs = 0
    
    def add_document(self, doc: Document) -> None:
        """Добавление документа в индекс"""
        self.documents[doc.id] = doc
        self.total_docs += 1
        
        # Простая токенизация (можно заменить на более сложную)
        terms = doc.text.lower().split()
        term_freq: Dict[str, int] = {}
        
        for term in terms:
            term_freq[term] = term_freq.get(term, 0) + 1
        
        for term, freq in term_freq.items():
            if term not in self.terms:
                self.terms[term] = {}
            self.terms[term][doc.id] = freq

class IndexManager:
    """Управление инвертированным индексом"""
    
    def __init__(self):
        self.index = InvertedIndex()
    
    def build_from_directory(self, directory_path: str) -> None:
        """Построение индекса из директории с текстовыми файлами"""
        # Реализация чтения файлов и построения индекса
        pass
    
    def save_index(self, filepath: str) -> None:
        """Сохранение индекса в файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'terms': self.index.terms,
                'documents': {k: v.__dict__ for k, v in self.index.documents.items()}
            }, f, ensure_ascii=False)
    
    def load_index(self, filepath: str) -> None:
        """Загрузка индекса из файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Восстановление индекса из JSON