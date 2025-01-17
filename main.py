import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import logging
import yaml
import sys
import time
import random
import undetected_chromedriver as udc
from telegram import Bot
import asyncio

load_dotenv()

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("/tmp/out.log"), logging.StreamHandler(sys.stdout)],
)


class Prenota:
    MAX_ATTEMPTS = 3  # Máximo número de intentos antes de esperar
    WAIT_TIME = 600    # 10 minutos en segundos (600 segundos)

    @staticmethod
    def check_file_exists(file_name):
        file_path = os.path.join(os.getcwd(), file_name)
        return os.path.isfile(file_path)

    @staticmethod
    def load_config(file_path):
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
        return config

    @staticmethod
    def check_for_dialog(driver):
        try:
            dialog = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            button_inside_dialog = dialog.find_element(
                By.XPATH, "//button[contains(text(),'ok')]"
            )
            button_inside_dialog.click()
            logging.info(
                f"Timestamp: {str(datetime.now())} - Scheduling is not available right now."
            )
            return True
        except NoSuchElementException:
            logging.info(
                f"Timestamp: {str(datetime.now())} - Element WlNotAvailable not found. Start filling the forms."
            )
            return False

    @staticmethod
    def fill_citizenship_form(driver, user_config):
        try:
            driver.get("https://prenotami.esteri.it/Services/Booking/1022")
            time.sleep(6)
            if not Prenota.check_for_dialog(driver):
                file_location = os.path.join("files/residencia.pdf")
                choose_file = driver.find_elements(By.ID, "File_0")
                choose_file[0].send_keys(file_location)
                privacy_check = driver.find_elements(By.ID, "PrivacyCheck")
                privacy_check[0].click()
                submit = driver.find_elements(By.ID, "btnAvanti")
                submit[0].click()
                with open("files/citizenship_form.html", "w") as f:
                    f.write(driver.page_source)
                return True
        except Exception as e:
            logging.info(f"Exception {e}")
            return False

    @staticmethod
    async def fill_passport_form(driver, user_config):
        try:
            time.sleep(10)
            driver.get("https://prenotami.esteri.it/Services/Booking/4950")
            time.sleep(5)

            if not Prenota.check_for_dialog(driver):
                await Prenota.send_message('hay turno!!!!!!!!!!!!!!!!!!! :)))))))')
               
                with open("files/passport_form.html", "w") as f:
                    f.write(driver.page_source)

                q0 = Select(driver.find_element(By.ID, "ddls_0"))
                q0.select_by_visible_text(user_config.get("possess_expired_passport"))

                q1 = Select(driver.find_element(By.ID, "ddls_1"))
                q1.select_by_visible_text(user_config.get("possess_expired_passport"))

                q2 = driver.find_element(By.ID, "DatiAddizionaliPrenotante_2___testo")
                q2.send_keys(user_config.get("total_children"))

                q3 = driver.find_element(By.ID, "DatiAddizionaliPrenotante_3___testo")
                q3.send_keys(user_config.get("full_address"))

                q4 = Select(driver.find_element(By.ID, "ddls_4"))
                q4.select_by_visible_text(user_config.get("marital_status"))

                time.sleep(1)

                file0 = driver.find_element(By.XPATH, '//*[@id="File_0"]')
                file0.send_keys(os.getcwd() + "/files/identidade.pdf")

                time.sleep(1)

                file1 = driver.find_element(By.XPATH, '//*[@id="File_1"]')
                file1.send_keys(os.getcwd() + "/files/residencia.pdf")

                checkBox = driver.find_element(By.ID, "PrivacyCheck")
                checkBox.click()

                form_submit = driver.find_element(By.ID, "btnAvanti")
                form_submit.click()

                return True
            else:
                #await Prenota.send_message('no turno')
                print('no turno')
        except Exception as e:
            logging.info(f"Exception {e}")
            return False
    @staticmethod
    async def send_message(message):
        try:
            TELEGRAM_TOKEN = '7828614620:AAF_iwuKAncATwOVzjumNHuSNhqw_Bg4xF8'
            CHAT_ID = '6674438880'

            bot = Bot(token=TELEGRAM_TOKEN)
            response = bot.send_message(chat_id=CHAT_ID, text=message)

            logging.info("Mensaje enviado: %s", message)
            logging.info("Contenido de respuesta: %s", response.text)  # Agregar esta línea
        except Exception as e:
            logging.error("Error al enviar mensaje: %s", e)

    @staticmethod
    async def run():
        #if Prenota.check_file_exists("files/residencia.pdf"):
        logging.info(
            f"Timestamp: {str(datetime.now())} - Required files available."
        )
        email = os.getenv("username")
        password = os.getenv("password")
        user_config = Prenota.load_config("parameters.yaml")
        print(user_config.get("full_address"))
        options = udc.ChromeOptions()
        options.headless = False
        #options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        options.add_argument("accept-language=en-US,en;q=0.9")
        options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-automation")
        



        driver = udc.Chrome(use_subprocess=True, options=options)
        driver.delete_all_cookies()
        


        try:
            driver.get("https://prenotami.esteri.it/")
            await asyncio.sleep(random.uniform(2, 4))  # Introducir un retraso aleatorio
            email_box = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "login-email"))
            )
            password_box = driver.find_element(By.ID, "login-password")
            email_box.send_keys(email)
            password_box.send_keys(password)
            # Simular movimientos del mouse
            await asyncio.sleep(random.uniform(2, 4))
            time.sleep(4)
            button = driver.find_elements(
                By.XPATH, "//button[contains(@class,'button primary g-recaptcha')]"
            )
            button[0].click()
            logging.info(
                f"Timestamp: {str(datetime.now())} - Successfully logged in."
            )
            time.sleep(10)
        except Exception as e:
            logging.info(f"Exception: {e}")

        attempt_counter = 0  # Inicializa el contador de intentos
        
        for i in range(200):
            random_number = random.randint(1, 5)

            if user_config["request_type"] == "carta":
                if await Prenota.fill_citizenship_form(driver, user_config):
                    break
            elif user_config["request_type"] == "passport":
                if await Prenota.fill_passport_form(driver, user_config):
                    break

            attempt_counter += 1  # Incrementa el contador en cada intento

            # Si hemos hecho 3 intentos, esperamos 10 minutos antes de continuar
            if attempt_counter >= Prenota.MAX_ATTEMPTS:
                logging.info(f"Esperando {Prenota.WAIT_TIME / 60} minutos antes de reintentar...")
                await asyncio.sleep(Prenota.WAIT_TIME)  # Esperar 10 minutos
                attempt_counter = 0  # Reinicia el contador de intentos

            await asyncio.sleep(random_number)


        user_input = input(
            f"Timestamp: {str(datetime.now())} - Go ahead and fill manually the rest of the process. "
            f"When finished, type quit to exit the program and close the browser. "
        )
        while True:
            if user_input == "quit":
                driver.quit()
                break
        #else:
        #    logging.info(
        #        "Required files are not available. Check the required files in README.md file. Ending execution."
        #    )
        #    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(Prenota.run())
    

