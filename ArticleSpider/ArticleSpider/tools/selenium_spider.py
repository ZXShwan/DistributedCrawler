# -*- coding: utf-8 -*-
__author__ = 'zx'
__date__ = '11/24/17 13:26'

from scrapy.selector import Selector
from selenium import webdriver
from settings import CHROME_EXE_PATH
import time

# browser = webdriver.Chrome(executable_path=CHROME_EXE_PATH)

zhihu_account = ""
zhihu_passwd = ""
sina_account = ""
sina_passwd = ""

if __name__ == '__main__':
    # 模拟知乎登录
    # browser.get("https://www.zhihu.com/#signin")
    # browser.find_element_by_css_selector(".qrcode-signin-step1 div.qrcode-signin-cut-button span").click()
    # browser.find_element_by_css_selector(".view-signin input[name='account']").send_keys(zhihu_account)
    # browser.find_element_by_css_selector(".view-signin input[name='password']").send_keys(zhihu_passwd)
    # browser.find_element_by_css_selector(".view-signin button.sign-button").click()

    # 模拟微博登录
    # browser.get("https://www.weibo.com")
    # time.sleep(10)
    # browser.find_element_by_css_selector("#loginname").send_keys(sina_account)
    # browser.find_element_by_css_selector(".info_list.password input[node-type='password']").send_keys(sina_passwd)
    # browser.find_element_by_css_selector(".info_list.login_btn a[node-type='submitBtn']").click()

    # 模拟鼠标下拉操作
    # browser.get("https://www.oschina.net/blog")
    # time.sleep(5)
    # for i in range(3):
    #     browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
    #     time.sleep(3)

    # browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.1.448d7ddcVX1EYj&id=558550356564&ns=1&abbucket=4&sku_properties=10004:709990523;5919063:6536025;12304035:3222911")
    # selector = Selector(text=browser.page_source)
    # print(selector.css(".tm-price::text").extract_first())

    # python virtual display
    # from pyvirtualdisplay import Display
    # display = Display(visible=0, size=(800, 600))
    # display.start()

    # 设置chromedriver不加载图片
    chrome_options = webdriver.ChromeOptions()
    chrome_prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    browser = webdriver.Chrome(executable_path=CHROME_EXE_PATH, chrome_options=chrome_options)
    browser.get("https://www.taobao.com")

    # browser.quit()
