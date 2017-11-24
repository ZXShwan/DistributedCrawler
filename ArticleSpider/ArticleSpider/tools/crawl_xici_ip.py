# -*- coding: utf-8 -*-
__author__ = 'zx'
__date__ = '11/19/17 23:24'
import requests
import MySQLdb
from scrapy.selector import Selector

conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="article_spider", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    # crawl ips from xicidaili.com and save to database for use
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
    for i in range(2538):
        response = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)

        selector = Selector(text=response.text)
        all_trs = selector.css("#ip_list tr")
        ip_list = []

        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract_first()
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_tr_text = tr.css("td::text").extract()
            ip = all_tr_text[0]
            port = all_tr_text[1]
            proxy_type = all_tr_text[5]
            if (not proxy_type == "HTTPS") and (not proxy_type == "HTTP"):
                proxy_type = "HTTP"
            ip_list.append((ip, port, speed, proxy_type))

        for info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', {2}, '{3}')".format(
                    info[0], info[1], info[2], info[3]
                )
            )
            conn.commit()


class RandomIP(object):
    def delete_ip(self, ip):
        """
        Delete invalid ip from database
        :param ip:
        :return:
        """
        delete_sql = """delete from proxy_ip WHERE ip='{0}'""".format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def is_ip_valid(self, ip, port):
        """
        Judge if the ip and port are valid
        :param ip:
        :param port:
        :return:
        """
        http_url = "http://www.baidu.com"
        http_proxy_url = "http://{0}:{1}".format(ip, port)
        https_proxy_url = "https://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": http_proxy_url,
                "https": https_proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except:
            print("Invalid ip and port!")
            self.delete_ip(ip)
            return False
        else:
            if response.status_code >= 200 and response.status_code < 300:
                print("Valid ip.")
                return True
            else:
                print("Invalid ip and port!")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        """
        Get a valid random ip from database
        :return:
        """
        random_sql = """SELECT ip, port, proxy_type FROM proxy_ip ORDER BY RAND() LIMIT 1"""
        cursor.execute(random_sql)
        for info in cursor.fetchall():
            ip = info[0]
            port = info[1]
            proxy_type = info[2]

            if self.is_ip_valid(ip, port):
                return "{0}://{1}:{2}".format(proxy_type, ip, port)
            else:
                return self.get_random_ip()


if __name__ == '__main__':
    # print(crawl_ips())
    random_ip = RandomIP()
    rip = random_ip.get_random_ip()
    print(rip)
