import re
from datetime import datetime


class Recording:
    def __init__(self, index, title, page_link, description, primary_video_link="", secondary_video_link="", **kwargs):
        self.index = index
        self.title = title
        self.page_link = page_link
        self.description = description
        self.primary_video_link = primary_video_link
        self.secondary_video_link = secondary_video_link
        self.time_datetime = self.parse_time()
        self.time_str = self.time_datetime.strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        s = (f"[{self.index}] {self.title}\n"
             f"{self.time_str}\n"
             f"{self.description}\n"
             f"page link: {self.page_link}\n"
             f"primary video (classroom) link: {self.primary_video_link}\n"
             f"secondary video (slides) link: {self.secondary_video_link}")
        return s

    def parse_time(self):
        pattern = re.compile(r"Meeting Start: (\d+)/(\d+)/(\d+) @ (\d+):(\d+) (AM|PM)")
        match = pattern.search(self.description)
        month = int(match.group(1))
        date = int(match.group(2))
        year = int(match.group(3))
        hour_12 = int(match.group(4))
        minute = int(match.group(5))
        am_pm = match.group(6)
        if am_pm == "PM" and hour_12 < 12:
            hour_24 = int(hour_12) + 12
        else:
            hour_24 = hour_12
        time = datetime(year, month, date, hour_24, minute)
        return time

    def to_json_dict(self):
        r_dict = {}
        keys = ["index", "title", "page_link", "description", "primary_video_link", "secondary_video_link", "time_str"]
        for key in keys:
            r_dict[key] = getattr(self, key)
        return r_dict
