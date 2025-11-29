import pytest
from src.utils.tokenizer import Tokenizer
from src.utils.file_utils import FileUtils

class TestTokenizer:
    def test_tokenize_basic(self):
        """Тест базовой токенизации"""
        tokens = Tokenizer.tokenize("Привет, мир!")
        assert tokens == ["привет", "мир"]
    
    def test_tokenize_empty(self):
        """Тест токенизации пустого текста"""
        tokens = Tokenizer.tokenize("")
        assert tokens == []
    
    def test_remove_stopwords(self):
        """Тест удаления стоп-слов"""
        tokens = ["это", "тестовый", "текст", "и", "пример"]
        filtered = Tokenizer.remove_stopwords(tokens)
        assert filtered == ["тестовый", "текст", "пример"]

class TestFileUtils:
    def test_validate_file_size(self, tmp_path):
        """Тест проверки размера файла"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("x" * 1024)  # 1KB файл
        
        assert FileUtils.validate_file_size(str(test_file), max_size_mb=1)