import os

from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes
from selenium import webdriver
from scrapy import signals
from selenium.webdriver import DesiredCapabilities


class SeleniumMiddleware(object):
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.binary_location = os.getenv('FIREFOX_BIN')
        options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        self.driver = webdriver.Firefox(capabilities=cap, executable_path=os.getenv('GECKODRIVER_PATH'), options=options)


    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        request.meta['driver'] = self.driver  # to access driver from response
        self.driver.get(request.url)
        body = to_bytes(self.driver.page_source)  # body must be of type bytes
        return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def spider_opened(self, spider):
        self.driver = webdriver.Firefox()

    def spider_closed(self, spider):
        self.driver.close()