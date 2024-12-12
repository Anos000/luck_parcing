from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
import csv
from datetime import datetime, timezone, timedelta

# Настройка Selenium
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

# Функция для инициализации браузера
def initialize_browser():
    print("Инициализация браузера...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver

# Функция для получения текущего времени по МСК
def get_msk_time():
    msk_timezone = timezone(timedelta(hours=3))  # МСК = UTC+3
    return datetime.now(msk_timezone).strftime("%Y-%m-%d %H:%M:%S")

# Функция для записи данных в CSV
def save_data_to_csv(item_type, item_value, msk_time):
    with open("history_parc_lucky.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([item_type, item_value, msk_time])

# Функция для мониторинга контейнера history
def monitor_history(driver):
    try:
        print("Начинаем мониторинг...")
        last_seen_item = None

        while True:
            try:
                # Переключаемся на iframe
                iframe = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='1play.gamedev-tech.cc/lucky/onewin']"))
                )
                driver.switch_to.frame(iframe)

                # Ожидаем загрузки элемента body
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body[style*='overflow: auto;']"))
                )

                # Ожидаем загрузки контейнера #history
                history = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "history"))
                )
                print("Контейнер #history найден!")

                # Получаем первый элемент из history
                first_item = history.find_element(By.CSS_SELECTOR, "[id^='history-item-']")
                item_type = first_item.get_attribute("type")
                item_value = first_item.text

                # Получаем текущее время по МСК
                msk_time = get_msk_time()

                # Проверяем, является ли элемент новым
                if (item_type, item_value) != last_seen_item:
                    print(f"Новый элемент: Тип={item_type}, Значение={item_value}, Время={msk_time}")
                    save_data_to_csv(item_type, item_value, msk_time)
                    last_seen_item = (item_type, item_value)

                # Возвращаемся к основному контенту
                driver.switch_to.default_content()

                # Небольшая пауза перед следующей проверкой
                time.sleep(2)

            except Exception as e:
                print(f"Ошибка при мониторинге: {e}")
                print(f"Текущий URL: {driver.current_url}")
                print(f"Page source:\n{driver.page_source}")
                break

    except Exception as e:
        print(f"Ошибка при инициализации мониторинга: {e}")

# Основной код
try:
    url = "https://1wzjvm.top/casino/play/1play_1play_luckyjet"
    # Записываем заголовки в CSV файл, если он пустой
    with open("history_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Type", "Value", "Time (MSK)"])

    driver = initialize_browser()
    monitor_history(driver)
except KeyboardInterrupt:
    print("Мониторинг остановлен пользователем.")
except Exception as e:
    print(f"Ошибка при работе Selenium: {e}")
    print(f"Stacktrace: {traceback.format_exc()}")
finally:
    if driver:
        driver.quit()
