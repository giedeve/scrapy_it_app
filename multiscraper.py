from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
# Import every spider
from scrapy_job_it.spiders.bdcrawler import BDcrawlerSpider
from scrapy_job_it.spiders.nfjcrawler import NfjcrawlerSpider

#settings = get_project_settings()
# process = CrawlerProcess()
# Insert a crawl process for every spider here
# process.crawl(BDcrawlerSpider)
# process.crawl(NfjcrawlerSpider)
# process.start()
configure_logging()
runner = CrawlerRunner()
@defer.inlineCallbacks
def crawl():
    yield runner.crawl(BDcrawlerSpider)
    yield runner.crawl(NfjcrawlerSpider)
    reactor.stop()

crawl()
reactor.run() # the script will block here until the last crawl call is finished