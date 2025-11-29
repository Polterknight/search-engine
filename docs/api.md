# API Documentation

## Core Modules

### IndexManager
Основной класс для управления инвертированным индексом.

```python
manager = IndexManager()
manager.build_from_directory("/path/to/documents")
manager.save_index("index.json")