import logging
from typing import Dict, List
from ..models.document import Document
from ..utils.file_utils import FileUtils

class InvertedIndex:
    """Инвертированный индекс для быстрого поиска"""
    
    def __init__(self):
        self.terms: Dict[str, Dict[str, int]] = {}
        self.documents: Dict[str, Document] = {}
        self.total_docs = 0
    
    def add_document(self, doc: Document) -> None:
        """Добавление документа в индекс"""
        logger = logging.getLogger(__name__)
        
        self.documents[doc.id] = doc
        self.total_docs += 1
        
        logger.debug(f"Добавление документа: {doc.id}, слов: {doc.term_count}")
        
        # Простая токенизация
        terms = doc.text.lower().split()
        term_freq: Dict[str, int] = {}
        
        for term in terms:
            term_freq[term] = term_freq.get(term, 0) + 1
        
        logger.debug(f"Найдено уникальных терминов: {len(term_freq)}")
        
        for term, freq in term_freq.items():
            if term not in self.terms:
                self.terms[term] = {}
            self.terms[term][doc.id] = freq

class IndexManager:
    """Управление инвертированным индексом"""
    
    def __init__(self):
        self.index = InvertedIndex()
        self.logger = logging.getLogger(__name__)
    
    def build_from_directory(self, directory_path: str) -> None:
        """Построение индекса из директории с текстовыми файлами"""
        self.logger.info(f"Начало индексации директории: {directory_path}")
        
        documents = FileUtils.read_documents_from_directory(directory_path)
        self.logger.info(f"Загружено документов для индексации: {len(documents)}")
        
        if not documents:
            self.logger.warning("Не найдено документов для индексации!")
            return
        
        for doc in documents:
            self.index.add_document(doc)
            
        self.logger.info(f"Индексация завершена. Документов в индексе: {self.index.total_docs}")
        self.logger.info(f"Уникальных терминов в индексе: {len(self.index.terms)}")
    
    def save_index(self, filepath: str) -> None:
        """Сохранение индекса в файл"""
        # ... существующий код ...
    
    def load_index(self, filepath: str) -> None:
        """Загрузка индекса из файла"""
        # ... существующий код ...
