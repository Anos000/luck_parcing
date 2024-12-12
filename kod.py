from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Настройка Selenium
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

url = "https://1wzjvm.top/casino/play/1play_1play_luckyjet"

def initialize_browser():
    print("Инициализация браузера...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver

def find_history_element(driver):
    print("Начинаем поиск элемента #history...")

    try:
        # Ожидание основного iframe
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='1play.gamedev-tech.cc/lucky/onewin']"))
        )
        print("Найден iframe с URL:", iframe.get_attribute("src"))

        # Переход в контекст iframe
        driver.switch_to.frame(iframe)

        # Ожидание загрузки контейнера body внутри iframe
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body[style*='overflow: auto;']"))
        )
        print("Внутри iframe найден body.")

        # Поиск элемента с id="history"
        history = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "history"))
        )
        print("Контейнер #history найден!")
        print("Содержимое #history:", history.get_attribute("outerHTML"))
    except Exception as e:
        print(f"Ошибка при поиске #history: {e}")

# Основной код
try:
    driver = initialize_browser()
    find_history_element(driver)
except KeyboardInterrupt:
    print("Операция остановлена пользователем.")
finally:
    driver.quit()
