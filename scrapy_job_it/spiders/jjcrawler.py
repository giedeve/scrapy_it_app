import os
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ..items import ScrapyJobItItem
from selenium.webdriver.common.keys import Keys
from scrapy.selector import Selector
import time


class JjcrawlerSpider(scrapy.Spider):
    name = 'jjcrawler'
    SCROLL_PAUSE_TIME = 0.5
    WRAPPER_SELECTOR = ".//a[@class='css-18rtd1e']"
    TABLE_LAYOUT = "//div[@class='css-1macblb']"  # must be keyborard reachable
    ITEM_SELECTOR = f"{WRAPPER_SELECTOR}/div[@class='css-xhufe5']" #Single item in offer list
    UPPER_ROW = "div[@class='css-qjm23f']"  # Upper row containing offer name and price
    BOTTOM_ROW = "div[@class='css-mih8cb']"  # Bottom row containing company name, city and tags
    options = webdriver.FirefoxOptions()
    options.binary_location = os.getenv('FIREFOX_BIN')
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    cap = DesiredCapabilities().FIREFOX
    cap["marionette"] = True
    driver = webdriver.Firefox(capabilities=cap, executable_path=os.getenv('GECKODRIVER_PATH'), options=options)


    def start_requests(self):
        yield SeleniumRequest(
            url="https://justjoin.it/",
            wait_time=3,
            callback=self.parse
        )

    def parse_position(self, content):
        # Content in form: 'position: absolute; left: 0px; top: 0px; height: 89px; width: 100%;'
        return int(content.split(";")[2].split(':')[1][:-2])

    def fetch_html(self, driver):
        html = driver.page_source
        return Selector(text=html)

    def parse(self, response):

        driver = response.meta['driver']
        driver.maximize_window()

        search_input = driver.find_element_by_xpath(self.TABLE_LAYOUT)

        last_height = driver.execute_script("return arguments[0].scrollHeight", search_input)

        # --------------------- FIND LAST ELEMENT TOP POSITION --------------------------------------
        driver.execute_script("arguments[0].scrollTo(0,arguments[0].scrollHeight)", search_input)

        time.sleep(self.SCROLL_PAUSE_TIME)

        response_obj = self.fetch_html(driver)

        offer_list = response_obj.xpath(f"{self.TABLE_LAYOUT}/div")

        last_element = offer_list.xpath(".//div[starts-with(@style,'position:')]")[-1]
        last_element_top_position = self.parse_position(last_element.xpath(".//@style").get())

        # Get back to top
        driver.execute_script("arguments[0].scrollTo(0,0)", search_input)

        time.sleep(self.SCROLL_PAUSE_TIME)

        last_top_position_seen = -1

        # ----------------------- SCROLL THROUGH THE PAGE UNTIL YOU REACH THE BOTTOM -------------------
        # check if last visible item's top position is the same as overall last item's position
        while last_top_position_seen < last_element_top_position:
            response_obj = self.fetch_html(driver)
            offer_list = response_obj.xpath(f"{self.TABLE_LAYOUT}/div")

            for item in offer_list.xpath(".//div[starts-with(@style,'position:')]"):
                item_pos = self.parse_position(item.xpath(".//@style").get())
                keywords = []
                for keyword in item.xpath(f"{self.ITEM_SELECTOR}/{self.BOTTOM_ROW}/div[@class='css-1ij7669']/div"):
                    keywords.append(keyword.xpath("normalize-space(.//text())").get())
                # If your current item position was seen in previous iteration -> ignore it
                if item_pos <= last_top_position_seen:
                    continue
                else:
                    offert = ScrapyJobItItem()
                    offert['title'] = item.xpath(f"normalize-space({self.ITEM_SELECTOR}/{self.UPPER_ROW}/div[@class='css-18hez3m']/div[@class='css-wjfk7i']/text())").get()
                    offert['salary_range'] = item.xpath(f"normalize-space({self.ITEM_SELECTOR}/{self.UPPER_ROW}/div[@class='css-v6uxww']/span/text())").get()
                    offert['company'] = item.xpath(f"normalize-space({self.ITEM_SELECTOR}/{self.BOTTOM_ROW}/div[@class='css-pdwro7']/div[@class='css-ajz12e']/text())").get()
                    offert['city'] = item.xpath(f"normalize-space({self.ITEM_SELECTOR}/{self.BOTTOM_ROW}/div[@class='css-pdwro7']/div[@class='css-1ihx907']/text())").get()
                    offert['keywords'] = keywords
                    offert['job_url'] = item.xpath(f"{self.WRAPPER_SELECTOR}").xpath(".//@href").get()
                    offert['scrapped'] = True
                    offert['still_active'] = True
                    offert['job_service'] = 'JustJoinIT'
                    yield offert
                    # yield {
                    #     'title': item.xpath(
                    #         f"normalize-space({self.ITEM_SELECTOR}/{self.UPPER_ROW}/div[@class='css-18hez3m']/div[@class='css-wjfk7i']/text())").get(),
                    #     'price range': item.xpath(
                    #         f"normalize-space({self.ITEM_SELECTOR}/{self.UPPER_ROW}/div[@class='css-v6uxww']/span/text())").get(),
                    #     'company': item.xpath(
                    #         f"normalize-space({self.ITEM_SELECTOR}/{self.BOTTOM_ROW}/div[@class='css-pdwro7']/div[@class='css-ajz12e']/text())").get(),
                    #     'city': item.xpath(
                    #         f"normalize-space({self.ITEM_SELECTOR}/{self.BOTTOM_ROW}/div[@class='css-pdwro7']/div[@class='css-1n50ecq']/text())").get(),
                    #     'keywords': keywords
                    # }

            # Get current view last element position
            last_element_seen = offer_list.xpath(".//div[starts-with(@style,'position:')]")[-1]
            last_top_position_seen = self.parse_position(last_element_seen.xpath(".//@style").get())

            search_input.send_keys(Keys.PAGE_DOWN)
            time.sleep(self.SCROLL_PAUSE_TIME)

