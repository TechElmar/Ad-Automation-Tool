import undetected_chromedriver as uc
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
import encodings.idna
from time import sleep


def getOptions():
    options = uc.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("disable-infobars")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    return options

def getDriver():
    driver = Chrome()
    return driver
