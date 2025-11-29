from typing import List
from ..models.document import SearchResult
from ..utils.tokenizer import Tokenizer
from .ranker import TFIDFRanker

class SearchManager:
    """Управление поисковыми запросами"""
    
    def __init__(self, index):
        self.index = index
        self.ranker = TFIDFRanker()
        self.tokenizer = Tokenizer()
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Выполняет поиск по запросу
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            List[SearchResult]: Отсортированные результаты поиска
        """
        if not query.strip():
            return []
            
        # Токенизация запроса
        query_tokens = self.tokenizer.tokenize(query)
        query_tokens = self.tokenizer.remove_stopwords(query_tokens)
        
        if not query_tokens:
            return []
            
        # Ранжирование документов
        results = self.ranker.rank(query_tokens, self.index, limit)
        return results
    
    def batch_search(self, queries: List[str]) -> List[List[SearchResult]]:
        """
        Пакетный поиск по нескольким запросам
        
        Args:
            queries: Список поисковых запросов
            
        Returns:
            List[List[SearchResult]]: Результаты для каждого запроса
        """
        return [self.search(query) for query in queries]