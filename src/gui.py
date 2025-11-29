import sys
import os
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Теперь импортируем абсолютными путями
from src.core.index_manager import IndexManager, InvertedIndex
from src.core.search_manager import SearchManager
from src.core.ranker import TFIDFRanker
from src.models.document import Document, SearchResult
from src.utils.tokenizer import Tokenizer
from src.utils.file_utils import FileUtils

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QTextEdit, QLineEdit, 
                           QListWidget, QLabel, QFileDialog, QProgressBar,
                           QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class SearchEngine:
    """Обертка для поискового движка"""
    def __init__(self):
        self.index_manager = IndexManager()
        self.search_manager = None
        
    def index_documents(self, directory_path):
        """Индексация документов"""
        self.index_manager.build_from_directory(directory_path)
        self.search_manager = SearchManager(self.index_manager.index)
        
    def search(self, query, limit=10):
        """Поиск по запросу"""
        if self.search_manager:
            return self.search_manager.search(query, limit)
        return []

class IndexingThread(QThread):
    """Поток для индексации документов"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path
        self.engine = SearchEngine()
        
    def run(self):
        try:
            self.engine.index_documents(self.directory_path)
            self.finished.emit(True, f"Индексация завершена. Документов: {self.engine.index_manager.index.total_docs}")
        except Exception as e:
            self.finished.emit(False, f"Ошибка индексации: {str(e)}")

class SearchEngineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = SearchEngine()
        self.current_indexed_folder = ""
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Простой поисковый движок")
        self.setGeometry(100, 100, 1000, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title_label = QLabel("ПРОСТОЙ ПОИСКОВЫЙ ДВИЖОК")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        self.select_folder_btn = QPushButton("Выбрать папку с документами")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_folder_btn.setMinimumHeight(35)
        
        self.selected_folder_label = QLabel("Папка не выбрана")
        self.selected_folder_label.setStyleSheet("color: gray; font-style: italic;")
        
        self.index_btn = QPushButton("Индексировать")
        self.index_btn.clicked.connect(self.start_indexing)
        self.index_btn.setMinimumHeight(35)
        self.index_btn.setEnabled(False)
        
        control_layout.addWidget(self.select_folder_btn)
        control_layout.addWidget(self.selected_folder_label)
        control_layout.addWidget(self.index_btn)
        control_layout.addStretch()
        
        main_layout.addLayout(control_layout)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - поиск и результаты
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Поисковая строка
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поисковый запрос:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите поисковый запрос...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Найти")
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setEnabled(False)
        search_layout.addWidget(self.search_btn)
        
        left_layout.addLayout(search_layout)
        
        # Результаты поиска
        left_layout.addWidget(QLabel("Результаты поиска:"))
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.show_document_content)
        left_layout.addWidget(self.results_list)
        
        # Правая панель - содержимое документа
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("Содержимое документа:"))
        self.document_content = QTextEdit()
        self.document_content.setReadOnly(True)
        right_layout.addWidget(self.document_content)
        
        # Добавляем панели в разделитель
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")
        
    def select_folder(self):
        """Выбор папки с документами"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Выберите папку с документами",
            str(Path.home())
        )
        
        if folder:
            self.current_indexed_folder = folder
            folder_name = os.path.basename(folder)
            self.selected_folder_label.setText(f"Выбрано: {folder_name}")
            self.selected_folder_label.setStyleSheet("color: green; font-weight: bold;")
            self.index_btn.setEnabled(True)
            self.statusBar().showMessage(f"Выбрана папка: {folder}")
            
    def start_indexing(self):
        """Запуск индексации"""
        if not self.current_indexed_folder:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку с документами")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # индикатор прогресса
        self.index_btn.setEnabled(False)
        self.search_btn.setEnabled(False)
        
        # Запуск индексации в отдельном потоке
        self.indexing_thread = IndexingThread(self.current_indexed_folder)
        self.indexing_thread.finished.connect(self.indexing_finished)
        self.indexing_thread.start()
        
        self.statusBar().showMessage("Идет индексация документов...")
        
    def indexing_finished(self, success, message):
        """Завершение индексации"""
        self.progress_bar.setVisible(False)
        self.index_btn.setEnabled(True)
        
        if success:
            self.engine = self.indexing_thread.engine
            self.search_btn.setEnabled(True)
            self.statusBar().showMessage(message)
            QMessageBox.information(self, "Успех", message)
        else:
            self.statusBar().showMessage("Ошибка индексации")
            QMessageBox.critical(self, "Ошибка", message)
            
    def perform_search(self):
        """Выполнение поиска"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите поисковый запрос")
            return
            
        if not self.engine.search_manager:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните индексацию документов")
            return
            
        try:
            self.results_list.clear()
            self.document_content.clear()
            
            results = self.engine.search(query)
            
            if not results:
                self.results_list.addItem("По запросу ничего не найдено")
                return
                
            for result in results:
                item_text = f"{result.document.id} (релевантность: {result.score:.3f})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, result)  # сохраняем результат
                self.results_list.addItem(item)
                
            self.statusBar().showMessage(f"Найдено документов: {len(results)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска: {str(e)}")
            
    def show_document_content(self, item):
        """Показ содержимого выбранного документа"""
        result = item.data(Qt.ItemDataRole.UserRole)
        if hasattr(result, 'document') and hasattr(result.document, 'text'):
            content = f"Документ: {result.document.id}\n"
            content += f"Релевантность: {result.score:.3f}\n"
            content += f"Сниппет: {result.snippet}\n\n"
            content += f"Полный текст:\n{result.document.text}"
            
            self.document_content.setText(content)
        else:
            self.document_content.setText("Не удалось загрузить содержимое документа")

def main():
    """Запуск графического интерфейса"""
    app = QApplication(sys.argv)
    app.setApplicationName("Поисковый движок")
    
    window = SearchEngineGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
