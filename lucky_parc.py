import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timezone, timedelta
import os

# Настройка Selenium
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')  # Отключение расширений для минимизации сбоев
options.add_argument('--remote-debugging-port=9222')

url = "https://1wzjvm.top/casino/play/1play_1play_luckyjet"

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

# Функция для записи данных в CSV файл
def save_data_to_csv(item_type, item_value, msk_time):
    with open("history_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([item_type, item_value, msk_time])

# Функция для проверки и обработки iframe
def switch_to_game_iframe(driver):
    try:
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='1play.gamedev-tech.cc/lucky/onewin']"))
        )
        driver.switch_to.frame(iframe)
        print("Переключились на iframe.")
    except Exception as e:
        print(f"Ошибка переключения на iframe: {e}")
        raise

# Функция для мониторинга элементов в контейнере #history
def monitor_history(driver):
    try:
        print("Начинаем мониторинг...")
        last_seen_item = None

        while True:
            try:
                # Переключаемся на iframe, если требуется
                switch_to_game_iframe(driver)

                # Ожидание загрузки контейнера #history
                history = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "history"))
                )
                print("Контейнер #history найден!")

                # Находим первый элемент внутри history
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

                # Возвращаемся к основному документу
                driver.switch_to.default_content()

                # Небольшая пауза перед следующей проверкой
                time.sleep(2)

            except Exception as e:
                print(f"Ошибка в процессе мониторинга: {e}")
                driver.switch_to.default_content()
                time.sleep(5)  # Делаем паузу перед повторной попыткой

    except Exception as e:
        print(f"Критическая ошибка при мониторинге: {e}")

# Основной код
if __name__ == "__main__":
    try:
        # Проверка, существует ли файл
        file_exists = os.path.isfile("history_data.csv")

        # Если файла нет, создаём с заголовками
        if not file_exists:
            with open("history_data.csv", mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Value", "Time (MSK)"])

        # Инициализация браузера и запуск мониторинга
        driver = initialize_browser()
        monitor_history(driver)

    except KeyboardInterrupt:
        print("Мониторинг остановлен пользователем.")

    except Exception as e:
        print(f"Ошибка в основной программе: {e}")

    finally:
        driver.quit()
        print("Браузер закрыт.")
