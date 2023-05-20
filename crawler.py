from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from cookie import COOKIE


class Crawler:
    def __init__(self, web_driver_path="./web_driver", wait_second=10):
        installation = ChromeDriverManager(path=web_driver_path).install()
        service = ChromeService(installation)
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(wait_second)

    def close(self):
        self.driver.quit()

    def login_by_cookie(self, cookie):
        self.driver.get("https://canvas.cmu.edu/404")
        self.driver.add_cookie(cookie)

    def crawl(self, url, course_cnt):
        driver = self.driver
        driver.get(url)
        driver.switch_to.frame("tool_content")
        crawled_cnt = 0
        while crawled_cnt < course_cnt:
            table = driver.find_element(By.ID, "detailsTable")
            courses = table.find_elements(By.CLASS_NAME, "detail-cell")
            crawled_cnt += len(courses)
            print(crawled_cnt)
            self.click_next()

    def click_next(self):
        next_btn = self.driver.find_element(By.ID, "nextPage")
        next_btn.click()


crawler = Crawler()
crawler.login_by_cookie(COOKIE)
crawler.crawl("https://canvas.cmu.edu/courses/33119/external_tools/467", 32)
crawler.close()
