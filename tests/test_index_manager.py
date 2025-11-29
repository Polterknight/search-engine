import pytest
import tempfile
import os
from src.core.index_manager import IndexManager, InvertedIndex
from src.models.document import Document

class TestInvertedIndex:
    def test_add_document(self):
        """Тест добавления документа в индекс"""
        index = InvertedIndex()
        doc = Document(id="doc1", text="hello world")
        
        index.add_document(doc)
        
        assert "hello" in index.terms
        assert "world" in index.terms
        assert index.total_docs == 1
    
    def test_term_frequency_calculation(self):
        """Тест подсчета частоты терминов"""
        index = InvertedIndex()
        doc = Document(id="doc1", text="hello hello world")
        
        index.add_document(doc)
        
        assert index.terms["hello"]["doc1"] == 2
        assert index.terms["world"]["doc1"] == 1

class TestIndexManager:
    def test_save_load_index(self):
        """Тест сохранения и загрузки индекса"""
        manager = IndexManager()
        doc = Document(id="test_doc", text="test content")
        manager.index.add_document(doc)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
            
        try:
            # Сохранение
            manager.save_index(temp_path)
            assert os.path.exists(temp_path)
            
            # Загрузка в новый менеджер
            new_manager = IndexManager()
            new_manager.load_index(temp_path)
            
            assert "test" in new_manager.index.terms
            assert "content" in new_manager.index.terms
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)