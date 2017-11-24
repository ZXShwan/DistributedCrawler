# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import os.path
import datetime
from scrapy.loader import ItemLoader
from items import ZhihuQuestionItem, ZhihuAnswerItem
try:
    from urllib import parse
except:
    import urlparse as parse
try:
    from PIL import Image
except:
    print("No Pillow lib installed")


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    # initial answer url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": agent,
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"
    }

    # enable cookies for zhihu spider
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        Get all urls of html page and continue crawling based on these urls
        If the form of url matches "/question/xxx", download and parse
        :param response:
        :return:
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x .startswith("https") else False, all_urls)
        for url in all_urls:
            match_re = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_re:
                # get question page, than handle it with "parse_question" function
                request_url = match_re.group(1)
                question_id = match_re.group(2)
                yield scrapy.Request(request_url, meta={"question_id": question_id},
                                     headers=self.headers, callback=self.parse_question)
                break
            else:
                # if it's not question page, continue track
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        question_id = int(response.meta.get("question_id"))
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
        item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0),
                             headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            ans_item = ZhihuAnswerItem()
            ans_item["zhihu_id"] = answer["id"]
            ans_item["url"] = answer["url"]
            ans_item["question_id"] = answer["question"]["id"]
            ans_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            ans_item["content"] = answer["content"] if "content" in answer else None
            ans_item["praise_num"] = answer["voteup_count"]
            ans_item["comments_num"] = answer["comment_count"]
            ans_item["create_time"] = answer["created_time"]
            ans_item["update_time"] = answer["updated_time"]
            ans_item["crawl_time"] = datetime.datetime.now()
            yield ans_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        """
        The entry of this spider
        :return:
        """
        return [scrapy.Request('https://www.zhihu.com/#signin', meta={'cookiejar': 1},
                               headers=self.headers, callback=self.get_paras)]

    def get_paras(self, response):
        """
        Get the parameters: xsrf and captcha url
        :param response:
        :return:
        """
        match_re = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
        if match_re:
            xsrf = (match_re.group(1))
        if xsrf:
            captcha_url = 'https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000)
            return [scrapy.Request(captcha_url, callback=self.login, headers=self.headers,
                                   meta={'cookiejar': response.meta['cookiejar'], 'xsrf': xsrf})]

    def login(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        # Show captcha by pillow
        try:
            im = Image.open('captcha.jpg')
            im.show()
        except:
            print(u'Please go to %s directory and open "captcha.jpg", then input' % os.path.abspath('captcha.jpg'))
        captcha = input("please input the captcha:\n->")
        xsrf = response.meta['xsrf']
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": xsrf,
            "phone_num": '9292488976',
            "password": 'admin123',
            "captcha": captcha
        }
        return [scrapy.FormRequest(
            url=post_url,
            headers=self.headers,
            formdata=post_data,
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.is_login
        )]

    def is_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url=url, meta={'cookiejar':response.meta['cookiejar']},
                                     dont_filter=True, headers=self.headers)
