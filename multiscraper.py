from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# Import every spider
from scrapy_job_it.spiders.bdcrawler import BDcrawlerSpider
from scrapy_job_it.spiders.nfjcrawler import NfjcrawlerSpider

#settings = get_project_settings()
process = CrawlerProcess()
# Insert a crawl process for every spider here
process.crawl(BDcrawlerSpider)
process.crawl(NfjcrawlerSpider)
process.start()
