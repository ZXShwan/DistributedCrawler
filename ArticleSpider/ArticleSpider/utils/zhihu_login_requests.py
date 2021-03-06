# -*- coding: utf-8 -*-
__author__ = 'zx'
__date__ = '11/15/17 16:02'

import re
import requests
import time
import os.path
try:
    import cookielib
except:
    import http.cookiejar as cookielib
try:
    from PIL import Image
except:
    print("No Pillow lib installed")


# build request headers
agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
headers = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    "User-Agent": agent
}
# use login cookie information
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("failed to load cookies")


def get_xsrf():
    """
    获取xsrf值
    :return:
    """
    response = session.get("https://www.zhihu.com", headers=headers)
    match_re = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_re:
        return (match_re.group(1))
    else:
        return ""


def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(t)
    response = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(response.content)
        f.close()
    # show captcha
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'Please go to %s directory and open "captcha.jpg", then input' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha:\n->")
    return captcha


def is_login():
    # find whether is login
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


def get_index():
    response = session.get("https://www.zhihu.com", headers=headers)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
        f.close()
    print("HTML page output done.")


def zhihu_login(account, password):
    """
    Main function to log in zhihu
    :param account:
    :param password:
    :return:
    """

    if re.match("1\d{10}", account):
        print("log in by phone number")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password
        }
    else:
        if "@" in account:
            print("log in by email")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password
            }
    login_page = session.post(post_url, data=post_data, headers=headers)
    login_code = login_page.json()
    print(login_code)
    if login_code['r'] == 1:
        # use captcha to log in
        post_data["captcha"] = get_captcha()
        login_page = session.post(post_url, data=post_data, headers=headers)
        login_code = login_page.json()
        print(login_code['msg'])

        session.cookies.save()


if __name__ == '__main__':
    if is_login():
        print("You have already log in!")
    else:
        zhihu_login("9292488976", "admin123")
    get_index()

