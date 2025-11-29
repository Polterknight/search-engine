#!/usr/bin/env python3
"""
Точка входа для командной строки
Алиас для main.py для обратной совместимости
"""

import sys
import os

# Добавляем путь к текущей директории
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == '__main__':
    main()
