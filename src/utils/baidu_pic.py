from contextlib import contextmanager
from urllib.request import urlretrieve
import uuid

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class Browser:
    def __init__(self):
        options = Options()
        options.add_argument('--headless=new')
        self.browser = webdriver.Chrome(options=options)

    def close(self):
        self.browser.quit()

    def download_pics(self, keyword, dst, total_pic=1):
        self.browser.get('https://image.baidu.com')
        e = self.browser.find_element(By.XPATH,'//input[@name="word"]')
        e.send_keys(keyword)

        btn = self.browser.find_element(By.XPATH,'//input[@value = "百度一下"]')
        btn.click()


        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="imgid"]/div[1]/ul')))

        li_list = self.browser.find_elements(
            By.XPATH, '//div[@id="imgid"]//li[@class="imgitem"]')
        size = min(len(li_list), total_pic)
        links = []
        for i in range(size):
            link = None
            for key in ('data-bigimgurl', 'data-thumburl', 'data-objurl'):
                link = li_list[i].get_attribute(key)
                if link:
                    links.append(link)
                    break
        path = []
        for i, link in enumerate(links):
            p = f'{dst}/{uuid.uuid4().hex}_{i}.jpeg'
            urlretrieve(link, p)
            path.append(p)
        return path


@contextmanager
def get_browser():
    browser = Browser()
    try:
        yield browser
    finally:
        browser.close()
