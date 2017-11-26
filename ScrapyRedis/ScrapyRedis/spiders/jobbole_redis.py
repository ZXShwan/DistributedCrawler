# -*- coding: utf-8 -*-
__author__ = 'zx'
__date__ = '11/26/17 14:20'

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from urllib import parse


class JobboleSpider(RedisSpider):
    name = 'jobbole'
    redis_key = 'jobbole:start_urls'
    allowed_domains = ['blog.jobbole.com']

    # 收集伯乐在线所有404的url以及404页面数
    handle_httpstatus_list = [404]

    def parse(self, response):
        """
        1. 获取文章列表页中文章的url，并交给scrapy下载后解析
        2. 获取下一页的url，并交给scrapy下载，下载完成后交给parse
        :param response:
        :return:
        """

        # 1. 获取文章列表页中文章的url，并交给scrapy下载后解析
        post_nodes = response.css("#archive div.floated-thumb .post-thumb a")
        for post_node in post_nodes:
            img_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front-img-url": img_url}, callback=self.parse_detail)

        # 2. 获取下一页的url，并交给scrapy下载，下载完成后交给parse
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        pass
