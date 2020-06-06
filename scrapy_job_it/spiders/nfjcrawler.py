# -*- coding: utf-8 -*-
import os
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ..items import ScrapyJobItItem
from scrapy.selector import Selector
import time


class NfjcrawlerSpider(scrapy.Spider):
    name = 'nfjcrawler'
    PAUSE_TIME = 1
    FIRST_COL = "./a/nfj-posting-item-title/div[@class='posting-title__wrapper']"
    SECOND_COL = "./a/div[@class='posting-info position-relative d-none d-lg-flex flex-grow-1']"
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
            url="https://nofluffjobs.com/jobs/backend?criteria=category%3Dbackend,frontend,fullstack,mobile,testing,devops,project-manager,support,business-intelligence,business-analyst,hr,it-trainee,ux,other&page=1",
            wait_time=5,
            callback=self.parse
        )

    def fetch_html(self, driver):
        html = driver.page_source
        return Selector(text=html)

    def parse(self, response):

        driver = response.meta['driver']
        driver.maximize_window()

        response_obj = self.fetch_html(driver)

        pagination = response_obj.xpath(".//ul[@class='pagination']")  # contains buttons
        buttons = []
        for button in pagination.xpath(".//li[@class='page-item']"):
            buttons.append(''.join(button.xpath("./a[@class='page-link']/text()").extract()))
        del buttons[-1]  # delete last button - it is empty
        last_button = int(buttons[-1])  # check number of last button

        for i in range(last_button):

            content_wrapper = response_obj.xpath(
                ".//div[@class='main-content__wrapper']/div/nfj-postings-search/div[@class='container mb-5']/nfj-main-loader/div[@class='mt-5']/nfj-search-results/nfj-postings-list")

            for item in content_wrapper.xpath(".//nfj-postings-item"):
                offert = ScrapyJobItItem()
                offert['title'] = item.xpath(f"normalize-space({self.FIRST_COL}/h4/text())").get()
                offert['salary_range'] = ''.join(item.xpath(
                    f"{self.SECOND_COL}/nfj-posting-item-tags/span[@class='text-truncate badgy salary btn btn-outline-secondary btn-sm']/text()").extract())
                offert['company'] = item.xpath(f"normalize-space({self.FIRST_COL}/span/text())").get().replace('in', '',
                                                                                                               1).replace(
                    'w ', '', 1)
                offert['city'] = item.xpath(
                    f"normalize-space({self.SECOND_COL}/span[@class='posting-info__location d-flex align-items-center ml-auto']/nfj-posting-item-city/text())").get()
                offert['keywords'] = ''.join(item.xpath(
                    "./a/div[@class='posting-info position-relative d-none d-lg-flex flex-grow-1']/nfj-posting-item-tags[@class='ml-3']/nfj-posting-item-tag/object/a/text()").extract())
                offert['job_url'] = item.xpath('./a/@href').get()
                offert['scrapped'] = True
                offert['still_active'] = True
                offert['job_service'] = 'NoFluffJobs'
                yield offert
                '''{
                    'title': item.xpath(f"normalize-space({self.FIRST_COL}/h4/text())").get(),
                    'price range': ''.join(item.xpath(
                        f"{self.SECOND_COL}/nfj-posting-item-tags/span[@class='text-truncate badgy salary btn btn-outline-secondary btn-sm']/text()").extract()),
                    'company': item.xpath(f"normalize-space({self.FIRST_COL}/span/text())").get().replace('in', '', 1),
                    'city': item.xpath(
                        f"normalize-space({self.SECOND_COL}/span[@class='posting-info__location d-flex align-items-center ml-auto']/nfj-posting-item-city/text())").get(),
                    'keywords': ''.join(item.xpath(
                        f"{self.SECOND_COL}/nfj-posting-item-tags/span[@class='text-truncate badgy technology btn btn-outline-secondary btn-sm']/text()").extract()),
                    'url': item.xpath('./a/@href').get()
                }'''

            # Go to the next page
            next_button = driver.find_element_by_xpath(
                ".//ul[@class='pagination']/li[@class='page-item active']/following-sibling::li[1]/a")
            driver.execute_script("arguments[0].click();", next_button)

            time.sleep(self.PAUSE_TIME)
            response_obj = self.fetch_html(driver)
