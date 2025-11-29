import pytest
from src.core.ranker import TFIDFRanker
from src.models.document import Document

class TestTFIDFRanker:
    def test_tfidf_calculation(self):
        """Тест корректности расчета TF-IDF"""
        ranker = TFIDFRanker()
        # Mock индекс и документы для тестирования
        # Проверка правильности подсчета scores
        
    def test_empty_query(self):
        """Тест обработки пустого запроса"""
        ranker = TFIDFRanker()
        results = ranker.rank([], None)
        assert len(results) == 0