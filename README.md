# Job Application Response Tracker v0.1

Простое приложение для отслеживания откликов на заявки о работе.

## Настройка проекта

### Клонирование репозитория
Сначала склонируйте репозиторий на ваш локальный компьютер:
```
git clone https://github.com/markbrutx/ApplicationTracker.git
```

### Настройка виртуального окружения
Для создания и активации виртуального окружения выполните следующие команды:

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS и Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Установка зависимостей
Установите все необходимые зависимости из файла `requirements.txt`:
```
pip install -r requirements.txt
```

## Запуск приложения

Для запуска приложения выполните:
```
python main.py
```

Следуйте инструкциям на экране для использования приложения.

# Если хотите собрать .exe
```
pyinstaller --onefile --windowed --icon=app_icon.ico --name=JobTrackerApp main.py
```