# Используем официальный Python-образ
FROM python:3.10-slim

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && apt-get clean

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска
CMD ["python", "lucky_parc.py"]
