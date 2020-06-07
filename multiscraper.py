from scrapy.crawler import CrawlerProcess
# Import every spider
from scrapy_job_it.spiders.bdcrawler import BDcrawlerSpider
from scrapy_job_it.spiders.nfjcrawler import NfjcrawlerSpider


process = CrawlerProcess()
# Insert a crawl process for every spider here
process.crawl(BDcrawlerSpider)
process.crawl(NfjcrawlerSpider)
process.start()
