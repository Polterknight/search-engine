import sys
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.file_utils import FileUtils

def test_directory_scan():
    """Тест сканирования директории"""
    test_dir = input("Введите путь к папке с документами: ").strip()
    
    if not test_dir:
        test_dir = "documents"  # Папка по умолчанию
    
    print(f"\n🔍 Сканируем папку: {test_dir}")
    
    if not os.path.exists(test_dir):
        print(f"❌ Папка {test_dir} не существует!")
        return
    
    # Показываем все файлы в папке
    all_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)
    
    print(f"📁 Всего файлов в папке: {len(all_files)}")
    for file in all_files:
        print(f"   - {file}")
    
    # Тестируем загрузку документов
    print(f"\n📖 Загружаем текстовые документы...")
    try:
        documents = FileUtils.read_documents_from_directory(test_dir)
        print(f"✅ Успешно загружено документов: {len(documents)}")
        
        for doc in documents:
            print(f"   - {doc.id} (символов: {len(doc.text)})")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    test_directory_scan()
