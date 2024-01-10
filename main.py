from crawler import Crawler
from cookie import COOKIE


URL = 'https://canvas.cmu.edu/courses/36223/external_tools/467'


def preview():
    """
    Preview and save results in JSON and HTML, download nothing
    """
    crawler = Crawler(headless=True)
    crawler.login_by_cookie(COOKIE)

    recordings = crawler.crawl_recordings(url=URL, reverse=True)
    for r in recordings:
        print(r)

    crawler.save_result()
    crawler.render_html()
    crawler.close()


def download():
    """
    Load results from saved JSON, download videos specified in JSON
    """
    crawler = Crawler(headless=True)
    crawler.login_by_cookie(COOKIE)

    crawler.load_result()
    crawler.download(1, 23)

    crawler.close()


preview()
download()
