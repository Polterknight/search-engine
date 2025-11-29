import os
import glob
from typing import List
from ..models.document import Document

class FileUtils:
    """Утилиты для работы с файлами"""
    
    @staticmethod
    def read_documents_from_directory(directory_path: str) -> List[Document]:
        """
        Читает все текстовые файлы из директории
        
        Args:
            directory_path: Путь к директории
            
        Returns:
            List[Document]: Список документов
            
        Raises:
            FileNotFoundError: Если директория не существует
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Директория {directory_path} не найдена")
            
        documents = []
        txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                doc_id = os.path.basename(file_path)
                documents.append(Document(id=doc_id, text=content))
                
            except UnicodeDecodeError:
                print(f"Ошибка чтения файла: {file_path}")
            except Exception as e:
                print(f"Ошибка обработки файла {file_path}: {e}")
                
        return documents

    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
        """
        Проверяет размер файла
        
        Args:
            file_path: Путь к файлу
            max_size_mb: Максимальный размер в МБ
            
        Returns:
            bool: True если размер допустимый
        """
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb <= max_size_mb