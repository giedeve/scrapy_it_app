# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyJobItItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    salary_range = scrapy.Field()
    company = scrapy.Field()
    city = scrapy.Field()
    keywords = scrapy.Field()
    job_url = scrapy.Field()
    scrappy_date = scrapy.Field()
    scrapped = scrapy.Field()
    still_active = scrapy.Field()
    job_service = scrapy.Field()
    hash_id = scrapy.Field()
    open_date = scrapy.Field()
    end_date = scrapy.Field()


