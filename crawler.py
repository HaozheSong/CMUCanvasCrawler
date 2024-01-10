import re
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jinja2 import Environment, FileSystemLoader
import requests

from recording import Recording


class Crawler:
    def __init__(self, wait_second=10, headless=False):
        """Crawler class initialization

        Args:
            wait_second (int, optional): 
                Time of waiting the HTML element to be loaded.
                Defaults to 10.
            headless (bool, optional): 
                Whether to Run the crawler in headless mode. 
                Defaults to False.
        """
        if headless:
            options = ChromeOptions()
            options.add_argument('--headless=new')
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome()
        self.wait_second = wait_second
        self.wait = WebDriverWait(self.driver, timeout=self.wait_second)
        self.recordings = []

    def close(self):
        self.driver.quit()

    def login_by_cookie(self, cookie):
        self.driver.get('https://canvas.cmu.edu/404')
        self.driver.add_cookie(cookie)

    def crawl_recordings(self, url, subfolder='', reverse=False):
        """Crawl all the recordings from the URL param

        Args:
            url (str): 
                The webpage to be crawled
            subfolder (str, optional): 
                Subfolder of the webpage. 
                There are probably multiple folders of a course, such as 18613 and 18213. 
                Specify '18613' or '18213' to crawl the specified recordings.
                Defaults to ''.
            reverse (bool, optional): 
                Whether to reverse the index of the crawled recordings. 
                Defaults to False.

        Returns:
            An array of Recording objects
        """
        recordings = []
        driver = self.driver
        driver.get(url)
        self.switch_to_frame('tool_content')
        if subfolder != '':
            self.click_subfolder_btn(subfolder)
        total = self.parse_page_range()['total']
        page_cnt = 0
        print(f'Start crawling recording pages 0/{total}')
        while page_cnt < total:
            self.parse_page_range()  # wait until the page is fully loaded
            cells_e = self.find_elements(By.CLASS_NAME, 'detail-cell')
            for e in cells_e:
                description_e = e.find_element(
                    By.CLASS_NAME, 'item-description')
                r_description = description_e.text
                detail_title_a_e = e.find_element(
                    By.CSS_SELECTOR, 'a.detail-title')
                r_link = detail_title_a_e.get_attribute('href')
                detail_title_span_e = detail_title_a_e.find_element(
                    By.TAG_NAME, 'span')
                r_title = detail_title_span_e.text
                if r_title == '' and r_link is None and r_description == '':
                    continue
                page_cnt += 1
                if reverse:
                    index = total + 1 - page_cnt
                else:
                    index = page_cnt
                r = Recording(index, r_title, r_link, r_description)
                recordings.append(r)
                print(f'Crawling recording pages {page_cnt}/{total}')
            if page_cnt < total:
                self.click_next(cells_e[0])
        if reverse:
            recordings.reverse()
        print(
            f'Start crawling primary and secondary video links from recording pages 0/{total}')
        for r in recordings:
            print(f'Crawling video links {r.index}/{total}')
            [primary_video_link, secondary_video_link] = self.find_videos_in_page(
                r.page_link)
            r.primary_video_link = primary_video_link
            r.secondary_video_link = secondary_video_link
        self.recordings = recordings
        print(recordings)
        return recordings

    def click_next(self, element):
        next_btn_e = self.find_element(By.ID, 'nextPage')
        next_btn_e.click()
        WebDriverWait(self.driver, self.wait_second).until(
            EC.staleness_of(element)
        )

    def click_subfolder_btn(self, btn_text):
        def text_in_btn(driver):
            buttons = driver.find_elements(By.CLASS_NAME, 'subfolder-item')
            for btn in buttons:
                if btn_text in btn.text:
                    btn.click()
                    return True
            return False

        self.wait.until(text_in_btn)

    def find_element(self, by, value):
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        return element

    def find_elements(self, by, value):
        elements = self.wait.until(
            EC.presence_of_all_elements_located((by, value)))
        return elements

    def switch_to_frame(self, frame_id):
        frame = self.wait.until(
            EC.frame_to_be_available_and_switch_to_it(frame_id))
        return frame

    def parse_page_range(self):
        self.wait.until(EC.text_to_be_present_in_element(
            (By.CLASS_NAME, 'MuiTablePagination-displayedRows'), 'of'))
        e = self.find_element(
            By.CLASS_NAME, 'MuiTablePagination-displayedRows')
        range_str = e.text
        pattern = re.compile(r'\d+')
        [start_index, end_index, total] = pattern.findall(range_str)
        recordings_this_page = int(end_index) - int(start_index) + 1
        page_range = {
            'start': int(start_index),
            'end': int(end_index),
            'recordings_this_page': recordings_this_page,
            'total': int(total)
        }
        return page_range

    def find_videos_in_page(self, page_link):
        # original_window = self.driver.current_window_handle
        # self.driver.switch_to.new_window('window')
        self.driver.get(page_link)
        primary_video_e = self.find_element(By.ID, 'primaryVideo')
        secondary_video_e = self.find_element(By.ID, 'secondaryVideo')
        primary_video_link = primary_video_e.get_attribute('src')
        secondary_video_link = secondary_video_e.get_attribute('src')
        # self.driver.close()
        # self.driver.switch_to.window(original_window)
        return [primary_video_link, secondary_video_link]

    def render_html(self):
        env = Environment(
            loader=FileSystemLoader(searchpath='./')
        )
        template = env.get_template('template.html')
        with open('result.html', 'w') as file:
            rendered_str = template.render(recordings=self.recordings)
            file.write(rendered_str)
        print('Results have been rendered to result.html')

    def save_result(self):
        with open('result.json', 'w') as file:
            json.dump([r.to_json_dict()
                      for r in self.recordings], file, indent=4)
        print('Results have been saved to result.json')

    def load_result(self):
        recordings = []
        with open('result.json', 'r') as file:
            json_list = json.load(file)
            for element in json_list:
                recording = Recording(**element)
                recordings.append(recording)
        self.recordings = recordings
        print('Results have been loaded from result.json')
        return recordings

    def download(self, start_index_included, num):
        """Download all recordings stored in the resulted `recordings` class attribute.

        Check the result.json or result.html to get the indexes of the recordings.
        Calling this method will download recordings with indexes from start_index_included
        to start_index_included+num-1.

        Args:
            start_index_included (int):
                The starting index of the recording to be downloaded.
            num (int):
                The number of the recordings to be downloaded.
        """
        # file_name = '{index}-{Classroom/Slide}-{time}'
        for i in range(num):
            index = start_index_included + i - 1
            recording = self.recordings[index]
            primary_video_name = f'{index + 1}-Classroom-{recording.time_filename}.mp4'
            secondary_video_name = f'{index + 1}-Slide-{recording.time_filename}.mp4'
            download_video(recording.primary_video_link, primary_video_name)
            download_video(recording.secondary_video_link,
                           secondary_video_name)


def download_video(url, filename):
    downloaded_bytes = 0
    with requests.get(url, stream=True) as request:
        size = float(request.headers['content-length'])
        with open(filename, 'wb') as file:
            for chunk in request.iter_content(chunk_size=8192):
                downloaded_bytes += len(chunk)
                print(f'Downloading {round(downloaded_bytes / size * 100, 2)}% '
                      f'{round(downloaded_bytes / 10 ** 6, 2)}MB/{round(size / 10 ** 6, 2)}/MB '
                      f'[{filename}]')
                file.write(chunk)
