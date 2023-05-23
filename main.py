from crawler import Crawler
from cookie import COOKIE

crawler = Crawler(headless=True)
# crawler.login_by_cookie(COOKIE)
# recordings = crawler.crawl_recordings("https://canvas.cmu.edu/courses/33119/external_tools/467")
# crawler.crawl_recordings("https://canvas.cmu.edu/courses/33277/external_tools/467", subfolder="18613")
# crawler.save_result()
recordings = crawler.load_result()
for r in recordings:
    print(r)
crawler.render_html()
crawler.download(0, 1)
crawler.close()
