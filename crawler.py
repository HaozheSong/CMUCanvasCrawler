import re
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
        self.wait = WebDriverWait(self.driver, timeout=self.wait_second)

    def close(self):
        self.driver.quit()

    def login_by_cookie(self, cookie):
        self.driver.get("https://canvas.cmu.edu/404")
        self.driver.add_cookie(cookie)

    def crawl_recordings(self, url):
        recordings = []
        driver = self.driver
        driver.get(url)
        self.switch_to_frame("tool_content")
        total = self.parse_page_range()["total"]
        crawled_cnt = 0
        while crawled_cnt < total:
            self.parse_page_range()  # wait until the page is fully loaded
            cells_e = self.find_elements(By.CLASS_NAME, "detail-cell")
            for e in cells_e:
                description_e = e.find_element(By.CLASS_NAME, "item-description")
                r_description = description_e.text
                detail_title_a_e = e.find_element(By.CSS_SELECTOR, "a.detail-title")
                r_link = detail_title_a_e.get_attribute("href")
                detail_title_span_e = detail_title_a_e.find_element(By.TAG_NAME, "span")
                r_title = detail_title_span_e.text
                if r_title == "" and r_link is None and r_description == "":
                    continue
                crawled_cnt += 1
                r = Recording(crawled_cnt, r_title, r_link, r_description)
                recordings.append(r)
                print(r)
            if crawled_cnt < total:
                self.click_next(cells_e[0])
        return recordings

    def click_next(self, element):
        next_btn_e = self.find_element(By.ID, "nextPage")
        next_btn_e.click()
        WebDriverWait(self.driver, self.wait_second).until(
            EC.staleness_of(element)
        )

    def find_element(self, by, value):
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        return element

    def find_elements(self, by, value):
        elements = self.wait.until(EC.presence_of_all_elements_located((by, value)))
        return elements

    def switch_to_frame(self, frame_id):
        frame = self.wait.until(EC.frame_to_be_available_and_switch_to_it(frame_id))
        return frame

    def parse_page_range(self):
        self.wait.until(EC.text_to_be_present_in_element((By.ID, "pageRange"), "Viewing"))
        e = self.find_element(By.ID, "pageRange")
        range_str = e.text
        pattern = re.compile(r'\d+')
        [start_index, end_index, total] = pattern.findall(range_str)
        recordings_this_page = int(end_index) - int(start_index) + 1
        page_range = {
            "start": int(start_index),
            "end": int(end_index),
            "recordings_this_page": recordings_this_page,
            "total": int(total)
        }
        return page_range


class Recording:
    def __init__(self, index, title, link, description):
        self.index = index
        self.title = title
        self.link = link
        self.description = description

    def __str__(self):
        s = (f"[{self.index}] {self.title}\n"
             f"{self.description}\n"
             f"{self.link}\n")
        return s


crawler = Crawler()
crawler.login_by_cookie(COOKIE)
crawler.crawl_recordings("https://canvas.cmu.edu/courses/33119/external_tools/467")
crawler.close()
