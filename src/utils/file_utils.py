import os
import glob
import logging
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
        """
        logger = logging.getLogger(__name__)
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Директория {directory_path} не найдена")
            
        documents = []
        
        # Ищем все .txt файлы в директории и поддиректориях
        pattern = os.path.join(directory_path, "**", "*.txt")
        txt_files = glob.glob(pattern, recursive=True)
        
        logger.info(f"Найдено .txt файлов: {len(txt_files)}")
        
        for file_path in txt_files:
            try:
                # Проверяем размер файла (макс 10 МБ)
                if not FileUtils.validate_file_size(file_path, max_size_mb=10):
                    logger.warning(f"Файл слишком большой: {file_path}")
                    continue
                
                # Читаем файл с обработкой разных кодировок
                content = FileUtils.read_file_safe(file_path)
                if content:
                    # Используем только имя файла (без пути) как ID
                    doc_id = os.path.basename(file_path)
                    documents.append(Document(id=doc_id, text=content))
                    logger.info(f"Успешно прочитан: {doc_id}")
                
            except Exception as e:
                logger.error(f"Ошибка чтения файла {file_path}: {e}")
                
        logger.info(f"Всего загружено документов: {len(documents)}")
        return documents

    @staticmethod
    def read_file_safe(file_path: str) -> str:
        """
        Безопасное чтение файла с обработкой разных кодировок
        """
        encodings = ['utf-8', 'cp1251', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                    if content:  # Проверяем что файл не пустой
                        return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
                
        logging.warning(f"Не удалось прочитать файл: {file_path}")
        return ""

    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
        """
        Проверяет размер файла
        """
        try:
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            return size_mb <= max_size_mb
        except:
            return False
