import re
from typing import List

class Tokenizer:
    """Простой токенизатор текста"""
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Разбивает текст на токены (слова)
        
        Args:
            text: Входной текст
            
        Returns:
            List[str]: Список токенов в нижнем регистре
        """
        # Удаляем знаки препинания и разбиваем на слова
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = clean_text.split()
        
        # Фильтруем пустые токены
        return [token for token in tokens if token.strip()]

    @staticmethod
    def remove_stopwords(tokens: List[str]) -> List[str]:
        """
        Удаляет стоп-слова из списка токенов
        
        Args:
            tokens: Список токенов
            
        Returns:
            List[str]: Токены без стоп-слов
        """
        stopwords = {'и', 'в', 'на', 'с', 'по', 'для', 'не', 'что', 'это', 'как'}
        return [token for token in tokens if token not in stopwords]