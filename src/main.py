#!/usr/bin/env python3
"""
Главный модуль поискового движка
Основная точка входа в программу
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.index_manager import IndexManager
from core.search_manager import SearchManager
from utils.file_utils import FileUtils

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('search_engine.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class SearchEngine:
    """Основной класс поискового движка"""
    
    def __init__(self):
        self.index_manager = IndexManager()
        self.search_manager = None
        
    def index_documents(self, directory_path: str, index_file: str = None):
        """
        Индексация документов в указанной директории
        
        Args:
            directory_path: Путь к директории с документами
            index_file: Путь для сохранения индекса (опционально)
        """
        try:
            logger.info(f"Начало индексации директории: {directory_path}")
            
            # Проверка существования директории
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Директория {directory_path} не существует")
            
            # Построение индекса
            self.index_manager.build_from_directory(directory_path)
            logger.info(f"Индексация завершена. Документов: {self.index_manager.index.total_docs}")
            
            # Сохранение индекса если указан файл
            if index_file:
                self.index_manager.save_index(index_file)
                logger.info(f"Индекс сохранен в файл: {index_file}")
            
            # Инициализация поискового менеджера
            self.search_manager = SearchManager(self.index_manager.index)
            
        except Exception as e:
            logger.error(f"Ошибка при индексации: {e}")
            raise
    
    def load_index(self, index_file: str):
        """
        Загрузка индекса из файла
        
        Args:
            index_file: Путь к файлу индекса
        """
        try:
            logger.info(f"Загрузка индекса из файла: {index_file}")
            self.index_manager.load_index(index_file)
            self.search_manager = SearchManager(self.index_manager.index)
            logger.info(f"Индекс загружен. Документов: {self.index_manager.index.total_docs}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке индекса: {e}")
            raise
    
    def search(self, query: str, limit: int = 10):
        """
        Выполнение поискового запроса
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            List[SearchResult]: Результаты поиска
        """
        if not self.search_manager:
            raise RuntimeError("Индекс не загружен. Сначала выполните индексацию или загрузку индекса.")
        
        try:
            logger.info(f"Выполнение поиска: '{query}'")
            results = self.search_manager.search(query, limit)
            logger.info(f"Найдено документов: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            raise
    
    def interactive_mode(self):
        """Интерактивный режим работы"""
        print("=== ПРОСТОЙ ПОИСКОВЫЙ ДВИЖОК ===")
        print("Режим: интерактивный")
        print("Команды: search, index, load, exit")
        print()
        
        while True:
            try:
                command = input("> ").strip().lower()
                
                if command == 'exit':
                    print("Завершение работы...")
                    break
                    
                elif command == 'index':
                    directory = input("Путь к директории с документами: ").strip()
                    if directory:
                        self.index_documents(directory)
                        print(f"Индексация завершена. Документов: {self.index_manager.index.total_docs}")
                    else:
                        print("Не указана директория")
                        
                elif command == 'load':
                    index_file = input("Путь к файлу индекса: ").strip()
                    if index_file:
                        self.load_index(index_file)
                        print(f"Индекс загружен. Документов: {self.index_manager.index.total_docs}")
                    else:
                        print("Не указан файл индекса")
                        
                elif command == 'search':
                    if not self.search_manager:
                        print("Сначала выполните индексацию (index) или загрузку индекса (load)")
                        continue
                        
                    query = input("Поисковый запрос: ").strip()
                    if query:
                        results = self.search(query)
                        if results:
                            print(f"Найдено документов: {len(results)}")
                            for i, result in enumerate(results, 1):
                                print(f"{i}. {result.document.id} (score: {result.score:.3f})")
                                print(f"   {result.snippet}")
                        else:
                            print("По запросу ничего не найдено")
                    else:
                        print("Не указан поисковый запрос")
                        
                elif command == 'help':
                    print("Доступные команды:")
                    print("  index  - индексация документов")
                    print("  load   - загрузка индекса из файла")
                    print("  search - выполнение поиска")
                    print("  exit   - выход из программы")
                    
                else:
                    print("Неизвестная команда. Введите 'help' для списка команд")
                    
            except KeyboardInterrupt:
                print("\nЗавершение работы...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")

def main():
    """Основная функция программы"""
    parser = argparse.ArgumentParser(
        description='Простой поисковый движок для текстовых документов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py index --dir ./documents
  python main.py search "поисковый запрос"
  python main.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Парсер для индексации
    index_parser = subparsers.add_parser('index', help='Индексация документов')
    index_parser.add_argument('--dir', required=True, help='Путь к директории с документами')
    index_parser.add_argument('--index-file', help='Файл для сохранения индекса')
    
    # Парсер для поиска
    search_parser = subparsers.add_parser('search', help='Поиск по индексу')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('--index-file', help='Файл индекса')
    search_parser.add_argument('--limit', type=int, default=10, help='Лимит результатов')
    
    # Парсер для интерактивного режима
    subparsers.add_parser('interactive', help='Интерактивный режим')
    
    args = parser.parse_args()
    
    # Создание экземпляра поискового движка
    engine = SearchEngine()
    
    try:
        if args.command == 'index':
            engine.index_documents(args.dir, args.index_file)
            print(f"✅ Индексация завершена. Документов: {engine.index_manager.index.total_docs}")
            
        elif args.command == 'search':
            if args.index_file:
                engine.load_index(args.index_file)
            elif not engine.search_manager:
                print("❌ Индекс не загружен. Укажите --index-file или сначала выполните индексацию")
                return
                
            results = engine.search(args.query, args.limit)
            if results:
                print(f"🔍 Найдено документов: {len(results)}")
                print()
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.document.id} (score: {result.score:.3f})")
                    print(f"   {result.snippet}")
                    print()
            else:
                print("❌ По запросу ничего не найдено")
                
        elif args.command == 'interactive':
            engine.interactive_mode()
            
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
