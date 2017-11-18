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
        with open('test.html', 'wb') as f:
            f.write(response.body)
            print('wirte finished!')
            f.close()
        pass

    def parse_detail(self, response):
        pass

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
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
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
