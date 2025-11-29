import argparse
from core.index_manager import IndexManager
from core.search_manager import SearchManager

def main():
    parser = argparse.ArgumentParser(description='Простой поисковый движок')
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Парсер для индексации
    index_parser = subparsers.add_parser('index', help='Индексация документов')
    index_parser.add_argument('--dir', required=True, help='Путь к директории с документами')
    index_parser.add_argument('--index-file', default='./index.json', help='Файл для сохранения индекса')
    
    # Парсер для поиска
    search_parser = subparsers.add_parser('search', help='Поиск по индексу')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('--index-file', default='./index.json', help='Файл индекса')
    search_parser.add_argument('--limit', type=int, default=10, help='Лимит результатов')
    
    args = parser.parse_args()
    
    if args.command == 'index':
        index_manager = IndexManager()
        index_manager.build_from_directory(args.dir)
        index_manager.save_index(args.index_file)
        print(f"Индексация завершена. Индекс сохранен в {args.index_file}")
    
    elif args.command == 'search':
        index_manager = IndexManager()
        index_manager.load_index(args.index_file)
        search_manager = SearchManager(index_manager.index)
        
        results = search_manager.search(args.query, args.limit)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.document.id} (score: {result.score:.3f})")
            print(f"   {result.snippet}\n")

if __name__ == '__main__':
    main()