import sys
import os
import logging
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.index_manager import IndexManager
from src.core.search_manager import SearchManager
from src.models.document import Document, SearchResult

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTextEdit, QLineEdit, 
    QListWidget, QLabel, QFileDialog, QProgressBar,
    QMessageBox, QSplitter, QListWidgetItem, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

class LogHandler(logging.Handler):
    """Кастомный обработчик логов для вывода в QTextBrowser"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                          datefmt='%H:%M:%S'))

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)
        # Автопрокрутка к последнему сообщению
        cursor = self.text_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_widget.setTextCursor(cursor)

class SearchEngine:
    """Обертка для поискового движка"""
    def __init__(self):
        self.index_manager = IndexManager()
        self.search_manager = None
        self.logger = logging.getLogger('SearchEngine')
        
    def index_documents(self, directory_path):
        """Индексация документов"""
        self.logger.info(f"Начало индексации директории: {directory_path}")
        self.index_manager.build_from_directory(directory_path)
        self.search_manager = SearchManager(self.index_manager.index)
        self.logger.info(f"Индексация завершена. Документов: {self.index_manager.index.total_docs}")
        
    def search(self, query, limit=10):
        """Поиск по запросу"""
        self.logger.info(f"Выполнение поиска: '{query}'")
        if self.search_manager:
            results = self.search_manager.search(query, limit)
            self.logger.info(f"Найдено документов: {len(results)}")
            return results
        return []

class IndexingThread(QThread):
    """Поток для индексации документов"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    
    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path
        self.engine = SearchEngine()
        
    def run(self):
        try:
            self.log_message.emit(f"🚀 Запуск индексации: {self.directory_path}")
            self.engine.index_documents(self.directory_path)
            self.log_message.emit("✅ Индексация успешно завершена")
            self.finished.emit(True, f"Индексация завершена. Документов: {self.engine.index_manager.index.total_docs}")
        except Exception as e:
            self.log_message.emit(f"❌ Ошибка индексации: {str(e)}")
            self.finished.emit(False, f"Ошибка индексации: {str(e)}")

class SearchEngineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = SearchEngine()
        self.current_indexed_folder = ""
        self.setup_logging()
        self.init_ui()
        
    def setup_logging(self):
        """Настройка системы логирования"""
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Простой поисковый движок")
        self.setGeometry(100, 100, 900, 700)
        
        # Создаем центральный виджет
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
        
        self.select_folder_btn = QPushButton("📁 Выбрать папку с документами")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_folder_btn.setMinimumHeight(35)
        
        self.selected_folder_label = QLabel("Папка не выбрана")
        self.selected_folder_label.setStyleSheet("color: gray; font-style: italic;")
        
        self.index_btn = QPushButton("⚡ Индексировать")
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
        
        # Поисковая строка
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Поисковый запрос:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите поисковый запрос...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Найти")
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setEnabled(False)
        self.search_btn.setMinimumHeight(35)
        search_layout.addWidget(self.search_btn)
        
        main_layout.addLayout(search_layout)
        
        # Основной разделитель (результаты + логи)
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Верхняя часть - результаты поиска
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        results_layout.addWidget(QLabel("📄 Результаты поиска (отсортированы по релевантности):"))
        self.results_list = QListWidget()
        results_layout.addWidget(self.results_list)
        
        # Нижняя часть - консоль логов
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        log_layout.addWidget(QLabel("📋 Консоль логов:"))
        self.log_console = QTextBrowser()
        self.log_console.setMaximumHeight(200)
        self.log_console.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New';
                font-size: 10pt;
            }
        """)
        
        # Настраиваем обработчик логов
        log_handler = LogHandler(self.log_console)
        logging.getLogger().addHandler(log_handler)
        
        log_layout.addWidget(self.log_console)
        
        # Кнопка очистки логов
        clear_layout = QHBoxLayout()
        self.clear_logs_btn = QPushButton("🧹 Очистить логи")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        clear_layout.addWidget(self.clear_logs_btn)
        clear_layout.addStretch()
        log_layout.addLayout(clear_layout)
        
        # Добавляем виджеты в основной разделитель
        main_splitter.addWidget(results_widget)
        main_splitter.addWidget(log_widget)
        main_splitter.setSizes([500, 200])
        
        main_layout.addWidget(main_splitter)
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")
        
        # Логируем запуск приложения
        logging.info("🚀 Приложение запущено")
        logging.info("📁 Выберите папку с документами для начала работы")
        
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
            logging.info(f"📁 Выбрана папка: {folder}")
            
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
        self.indexing_thread.log_message.connect(self.add_log_message)
        self.indexing_thread.start()
        
        self.statusBar().showMessage("Идет индексация документов...")
        
    def add_log_message(self, message):
        """Добавление сообщения в консоль логов"""
        logging.info(message)
        
    def indexing_finished(self, success, message):
        """Завершение индексации"""
        self.progress_bar.setVisible(False)
        self.index_btn.setEnabled(True)
        
        if success:
            self.engine = self.indexing_thread.engine
            self.search_btn.setEnabled(True)
            self.statusBar().showMessage(message)
            logging.info("✅ Готово! Можно выполнять поиск")
            QMessageBox.information(self, "Успех", message)
        else:
            self.statusBar().showMessage("Ошибка индексации")
            logging.error("❌ Индексация завершилась с ошибкой")
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
            
            logging.info(f"🔍 Выполнение поиска: '{query}'")
            results = self.engine.search(query)
            
            if not results:
                item = QListWidgetItem("❌ По запросу ничего не найдено")
                self.results_list.addItem(item)
                logging.info("❌ По запросу ничего не найдено")
                return
                
            for i, result in enumerate(results, 1):
                # Форматируем вывод с цветами в зависимости от релевантности
                score = result.score
                if score > 0.8:
                    score_text = f"🔥 {score:.3f}"
                elif score > 0.5:
                    score_text = f"⚡ {score:.3f}"
                else:
                    score_text = f"📊 {score:.3f}"
                
                item_text = f"{i}. {result.document.id} - релевантность: {score_text}"
                item = QListWidgetItem(item_text)
                
                # Устанавливаем цвет в зависимости от релевантности
                if score > 0.8:
                    item.setBackground(Qt.GlobalColor.green)
                    item.setForeground(Qt.GlobalColor.white)
                elif score > 0.5:
                    item.setBackground(Qt.GlobalColor.yellow)
                
                self.results_list.addItem(item)
                
            self.statusBar().showMessage(f"Найдено документов: {len(results)}")
            logging.info(f"✅ Найдено документов: {len(results)}")
            
        except Exception as e:
            error_msg = f"Ошибка поиска: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "Ошибка", error_msg)
            
    def clear_logs(self):
        """Очистка консоли логов"""
        self.log_console.clear()
        logging.info("🧹 Консоль логов очищена")

def main():
    """Запуск графического интерфейса"""
    app = QApplication(sys.argv)
    app.setApplicationName("Поисковый движок")
    
    window = SearchEngineGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
