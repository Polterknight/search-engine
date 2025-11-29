import pytest
import tempfile
import os
from src.core.index_manager import IndexManager
from src.core.search_manager import SearchManager
from src.utils.file_utils import FileUtils

class TestIntegration:
    def test_full_workflow(self):
        """Тест полного цикла: индексация -> поиск"""
        # Создаем временные файлы для тестирования
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем тестовые документы
            doc1_path = os.path.join(temp_dir, "doc1.txt")
            doc2_path = os.path.join(temp_dir, "doc2.txt")
            
            with open(doc1_path, 'w', encoding='utf-8') as f:
                f.write("прогноз погоды в москве на завтра")
                
            with open(doc2_path, 'w', encoding='utf-8') as f:
                f.write("новости технологий и искусственный интеллект")
            
            # Индексация
            index_manager = IndexManager()
            index_manager.build_from_directory(temp_dir)
            
            # Поиск
            search_manager = SearchManager(index_manager.index)
            results = search_manager.search("погода москва")
            
            assert len(results) >= 1
            assert results[0].document.id == "doc1.txt"