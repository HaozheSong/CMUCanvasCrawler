from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cookie import COOKIE


class Crawler:
    def __init__(self, web_driver_path="./web_driver", wait_second=10):
        installation = ChromeDriverManager(path=web_driver_path).install()
        service = ChromeService(installation)
        self.driver = webdriver.Chrome(service=service)
        self.wait_second = wait_second

    def close(self):
        self.driver.quit()

    def login_by_cookie(self, cookie):
        self.driver.get("https://canvas.cmu.edu/404")
        self.driver.add_cookie(cookie)

    def crawl(self, url, course_cnt):
        driver = self.driver
        driver.get(url)
        self.switch_to_frame("tool_content")
        crawled_cnt = 0
        while crawled_cnt < course_cnt:
            table = self.find_element(By.ID, "detailsTable")
            courses = table.find_elements(By.CLASS_NAME, "detail-cell")
            crawled_cnt += len(courses)
            print(crawled_cnt)
            if crawled_cnt < course_cnt:
                self.click_next(courses[0])

    def click_next(self, element):
        next_btn = self.find_element(By.ID, "nextPage")
        next_btn.click()
        WebDriverWait(self.driver, self.wait_second).until(
            EC.staleness_of(element)
        )

    def find_element(self, by, value):
        element = WebDriverWait(self.driver, self.wait_second).until(
            EC.presence_of_element_located((by, value))
        )
        return element

    def switch_to_frame(self, frame_id):
        element = WebDriverWait(self.driver, self.wait_second).until(
            EC.frame_to_be_available_and_switch_to_it(frame_id)
        )
        return element


crawler = Crawler()
crawler.login_by_cookie(COOKIE)
crawler.crawl("https://canvas.cmu.edu/courses/33119/external_tools/467", 32)
crawler.close()
