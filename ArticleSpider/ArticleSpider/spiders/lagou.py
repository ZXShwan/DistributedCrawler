# -*- coding: utf-8 -*-
import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from items import LagouJobItemLoader, LagouJobItem
from utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 1,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'user_trace_token=20171120044929-230976a8-cd6b-11e7-9969-5254005c3644; LGUID=20171120044929-23097abd-cd6b-11e7-9969-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_search; JSESSIONID=ABAAABAACBHABBI3F5E986C34E5C9C035773CEB6EE2A4EA; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_python%3FlabelWords%3D%26fromSearch%3Dtrue%26suginput%3D; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2F3602030.html; SEARCH_ID=51da9b4b13494237904557b81b5965f6; _gid=GA1.2.1628359507.1511124568; _ga=GA1.2.1734151622.1511124568; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1511124569; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1511131961; LGSID=20171120063341-b204b890-cd79-11e7-9958-525400f775ce; LGRID=20171120065259-63e786ca-cd7c-11e7-9969-5254005c3644',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
    }

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        """
        parse jobs in lagou.com
        :param response:
        :return:
        """
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_obj_id", get_md5(response.url))
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_value("crawl_time", datetime.datetime.now())

        job_item = item_loader.load_item()
        return job_item
