import pytest
from src.core.search_manager import SearchManager
from src.core.index_manager import InvertedIndex
from src.models.document import Document

class TestSearchManager:
    @pytest.fixture
    def sample_index(self):
        """Создает тестовый индекс"""
        index = InvertedIndex()
        index.add_document(Document(id="doc1", text="прогноз погоды в москве"))
        index.add_document(Document(id="doc2", text="новости технологий и it"))
        index.add_document(Document(id="doc3", text="погода в санкт-петербурге"))
        return index
    
    def test_search_basic(self, sample_index):
        """Тест базового поиска"""
        manager = SearchManager(sample_index)
        results = manager.search("погода")
        
        assert len(results) == 2
        assert results[0].document.id in ["doc1", "doc3"]
    
    def test_search_empty_query(self, sample_index):
        """Тест поиска с пустым запросом"""
        manager = SearchManager(sample_index)
        results = manager.search("")
        
        assert len(results) == 0
    
    def test_search_no_results(self, sample_index):
        """Тест поиска без результатов"""
        manager = SearchManager(sample_index)
        results = manager.search("несуществующее слово")
        
        assert len(results) == 0