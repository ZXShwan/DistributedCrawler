# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import os.path
try:
    from PIL import Image
except:
    print("No Pillow lib installed")


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": agent
    }

    def parse(self, response):
        pass

    def parse_detail(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def login(self, response):
        match_re = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
        if match_re:
            xsrf = (match_re.group(1))
        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": '17735132578',
                "password": 'Zx19940208',
                "captcha": ''
            }
            captcha_url = 'https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000)
            return [scrapy.FormRequest(
                url=post_url,
                headers=self.headers,
                formdata=post_data,
                meta={'post_data': post_data},
                callback=self.is_login
            )]

    def login_use_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        # 用pillow的Image显示验证码
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = input("please input the captcha:\n->")
        post_data = response.meta.get('post_data', {})
        post_data['captcha'] = captcha
        post_url = "https://www.zhihu.com/login/phone_num"
        return [scrapy.FormRequest(
            url=post_url,
            headers=self.headers,
            formdata=post_data,
            callback=self.is_login
        )]

    def is_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
