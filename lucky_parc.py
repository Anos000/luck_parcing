import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timezone, timedelta
import os  # Для проверки существования файла
from selenium.webdriver.chrome.options import Options
# Настройка Selenium
def initialize_browser():
    options = Options()
    options.add_argument('--headless')  # Run headlessly (optional)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/google-chrome-stable"  # Ensure this points to the installed Chrome binary

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Функция для получения текущего времени по МСК
def get_msk_time():
    msk_timezone = timezone(timedelta(hours=3))  # МСК = UTC+3
    return datetime.now(msk_timezone).strftime("%Y-%m-%d %H:%M:%S")

# Функция для записи данных в CSV файл
def save_data_to_csv(item_type, item_value, msk_time):
    with open("history_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        # Записываем строку с типом, значением и временем
        writer.writerow([item_type, item_value, msk_time])

# Функция для мониторинга элементов в контейнере #history
def monitor_history(driver):
    try:
        print("Начинаем мониторинг...")

        last_seen_item = None  # Для отслеживания последнего уникального элемента

        while True:
            try:
                # Переключаемся на iframe
                iframe = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='1play.gamedev-tech.cc/lucky/onewin']"))
                )
                driver.switch_to.frame(iframe)

                # Ожидание загрузки body
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body[style*='overflow: auto;']"))
                )

                # Ожидание загрузки контейнера #history
                history = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "history"))
                )
                print("Контейнер #history найден!")

                # Находим первый элемент внутри history (новый элемент всегда сверху)
                first_item = history.find_element(By.CSS_SELECTOR, "[id^='history-item-']")
                item_type = first_item.get_attribute("type")
                item_value = first_item.text

                # Получаем текущее время по МСК
                msk_time = get_msk_time()

                # Проверяем, является ли элемент новым
                if (item_type, item_value) != last_seen_item:
                    print(f"Новый элемент: Тип={item_type}, Значение={item_value}, Время={msk_time}")
                    # Сохраняем новый элемент в файл
                    save_data_to_csv(item_type, item_value, msk_time)
                    last_seen_item = (item_type, item_value)

                # Возвращаемся к основному документу
                driver.switch_to.default_content()

                # Небольшая пауза перед следующей проверкой
                time.sleep(2)

            except Exception as e:
                print(f"Ошибка при мониторинге: {e}")
                break

    except Exception as e:
        print(f"Ошибка при инициализации мониторинга: {e}")

# Основной код
try:
    # Проверка, существует ли файл
    file_exists = os.path.isfile("history_data.csv")

    # Открытие файла для записи заголовков только если файл не существует
    if not file_exists:
        with open("history_data.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Value", "Time (MSK)"])  # Записываем заголовки

    driver = initialize_browser()
    monitor_history(driver)
except KeyboardInterrupt:
    print("Мониторинг остановлен пользователем.")
finally:
    driver.quit()
