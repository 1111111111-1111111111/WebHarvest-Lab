import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


class loads_successfully:
    def __init__(self):
        pass

    def load_selenium(self,url):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')

        service = Service(r"D:\python_pro\chromedriver\chromedriver.exe")
        driver = webdriver.Chrome(service=service , options=options)
        driver.get(url)
        result = WebDriverWait(driver,timeout=30).until(EC.presence_of_element_located((By.CLASS_NAME, 'entry-title')))

        driver.quit()
        return result
if __name__ == '__main__':
    sele = loads_successfully()
    url = "https://doaenews.doae.go.th/"
    if sele.load_selenium(url):
        print("加载成功！")
    else:
        print("拒绝访问")