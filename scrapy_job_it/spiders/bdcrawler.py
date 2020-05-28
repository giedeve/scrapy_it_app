# -*- coding: utf-8 -*-
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from ..items import ScrapyJobItItem
from selenium.webdriver.common.keys import Keys
from scrapy.selector import Selector
import time


class BDcrawlerSpider(scrapy.Spider):
    name = 'bdcrawler'
    PAUSE_TIME = 1
    JOB_DETAILS_DIV = "./div[@class='job-details']"
    META_DIV = "div[@class='meta']"
    driver = webdriver.Firefox(executable_path="'geckodriver")
    def start_requests(self):
        yield SeleniumRequest(
            url="https://bulldogjob.com/companies/jobs?page=1",
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
        for button in pagination.xpath(".//li"):
            buttons.append(''.join(button.xpath("./a/text()").extract()))

        for i, button in enumerate(buttons):
            if button == '':
                del buttons[i]

        last_button = int(buttons[-1])  # check number of last button

        for i in range(last_button):

            content_wrapper = response_obj.xpath(
                ".//section[@class='search-results']/ul[starts-with(@class,'results-list')]")

            for item in content_wrapper.xpath(".//a[starts-with(@class,'job-item')]"):
                offert = ScrapyJobItItem()
                offert['title'] = item.xpath(f"normalize-space({self.JOB_DETAILS_DIV}/div[@class='title']/h2/text())").get()
                offert['salary_range'] = ''.join(
                        item.xpath(f"{self.JOB_DETAILS_DIV}/{self.META_DIV}/div[@class='salary']/text()").extract())
                offert['company'] = item.xpath(
                        f"normalize-space({self.JOB_DETAILS_DIV}/{self.META_DIV}/div[@class='company']/text())").get()
                offert['city'] = item.xpath(
                        f"normalize-space({self.JOB_DETAILS_DIV}/{self.META_DIV}/div[@class='location']//following-sibling::text())").get()

                offert['keywords'] = item.xpath(
                        "./div[@class='technologies']/ul[@class='tags']/child::li/div/text()").extract()
                offert['job_url'] = item.xpath('.//@href').get()
                offert['scrapped'] = True
                offert['still_active'] = True
                offert['job_service'] = 'BulldogJob'
                yield offert
                # yield {
                #     'title': item.xpath(f"normalize-space({self.JOB_DETAILS_DIV}/div[@class='title']/h2/text())").get(),
                #     'price range': ''.join(
                #         item.xpath(f"{self.JOB_DETAILS_DIV}/{self.META_DIV}/div[@class='salary']/text()").extract()),
                #     'company': item.xpath(
                #         f"normalize-space({self.JOB_DETAILS_DIV}/{self.META_DIV}/div[@class='company']/text())").get(),
                #     'city': item.xpath(
                #         f"normalize-space({self.JOB_DETAILS_DIV}/{self.META_DIV}/div[@class='location']//following-sibling::text())").get(),
                #     'keywords': item.xpath(
                #         "./div[@class='technologies']/ul[@class='tags']/child::li/div/text()").extract(),
                #     'url': item.xpath('.//@href').get()
                # }

            # Go to the next page
            next_button = driver.find_element_by_xpath(
                ".//ul[@class='pagination']/li[@class='active']/following-sibling::li[1]/a")
            driver.execute_script("arguments[0].click();", next_button)

            time.sleep(self.PAUSE_TIME)
            response_obj = self.fetch_html(driver)