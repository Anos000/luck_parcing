import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timezone, timedelta
import os  # Для проверки существования файла
import time

# Настройка логирования
logging.basicConfig(
    filename="monitoring.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Настройка Selenium
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

url = "https://1wzjvm.top/casino/play/1play_1play_luckyjet"

# Функция для инициализации браузера
def initialize_browser():
    logging.info("Инициализация браузера...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver

# Функция для получения текущего времени по МСК
def get_msk_time():
    msk_timezone = timezone(timedelta(hours=3))  # МСК = UTC+3
    return datetime.now(msk_timezone).strftime("%Y-%m-%d %H:%M:%S")

# Функция для записи данных в CSV файл
def save_data_to_csv(item_type, item_value, msk_time):
    try:
        with open("history_data.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([item_type, item_value, msk_time])
            logging.info(f"Данные записаны: Тип={item_type}, Значение={item_value}, Время={msk_time}")
    except Exception as e:
        logging.error(f"Ошибка записи в CSV: {e}")

# Функция для мониторинга элементов в контейнере #history
def monitor_history(driver):
    try:
        logging.info("Начинаем мониторинг...")
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

                # Находим первый элемент внутри history
                first_item = history.find_element(By.CSS_SELECTOR, "[id^='history-item-']")
                item_type = first_item.get_attribute("type")
                item_value = first_item.text

                # Получаем текущее время по МСК
                msk_time = get_msk_time()

                # Проверяем, является ли элемент новым
                if (item_type, item_value) != last_seen_item:
                    logging.info(f"Новый элемент: Тип={item_type}, Значение={item_value}, Время={msk_time}")
                    save_data_to_csv(item_type, item_value, msk_time)
                    last_seen_item = (item_type, item_value)

                # Возвращаемся к основному документу
                driver.switch_to.default_content()

                # Небольшая пауза перед следующей проверкой
                time.sleep(2)

            except Exception as e:
                logging.warning(f"Ошибка при мониторинге: {e}")
                time.sleep(5)  # Пауза перед повтором в случае ошибки

    except Exception as e:
        logging.error(f"Ошибка при инициализации мониторинга: {e}")

# Основной код
try:
    # Проверка, существует ли файл
    file_exists = os.path.isfile("history_data.csv")

    # Открытие файла для записи заголовков только если файл не существует
    if not file_exists:
        with open("history_data.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Value", "Time (MSK)"])  # Записываем заголовки

    driver = initialize_browser()
    monitor_history(driver)
except KeyboardInterrupt:
    logging.info("Мониторинг остановлен пользователем.")
except Exception as e:
    logging.critical(f"Критическая ошибка: {e}", exc_info=True)
finally:
    try:
        driver.quit()
        logging.info("Браузер закрыт.")
    except Exception as e:
        logging.error(f"Ошибка при закрытии браузера: {e}")
