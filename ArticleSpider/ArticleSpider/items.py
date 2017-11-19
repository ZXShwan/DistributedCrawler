# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime
# import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import extract_nums
from ArticleSpider.settings import SQL_DATE_FORMAT, SQL_DATETIME_FORMAT


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def remove_comment_tags(value):
    """
    去掉获取到的tags中提取的"评论"元素
    :param value:
    :return:
    """

    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    """
    自定义ItemLoader, 只获取list中第一个元素
    """

    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    url = scrapy.Field()
    url_obj_id = scrapy.Field()
    front_img_url = scrapy.Field(output_processor=MapCompose(return_value))
    front_img_path = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field(input_processor=MapCompose(date_convert))
    praise_nums = scrapy.Field(input_processor=MapCompose(extract_nums))
    fav_nums = scrapy.Field(input_processor=MapCompose(extract_nums))
    comment_nums = scrapy.Field(input_processor=MapCompose(extract_nums))
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )

    def get_insert_sql(self):
        insert_sql = """insert into jobbole_article(title, create_date, url, url_obj_id, front_img_url, front_img_path,
                                  praise_nums, fav_nums, comment_nums, content, tags)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE praise_nums=VALUES(praise_nums), fav_nums=VALUES(fav_nums),
                        comment_nums=VALUES(comment_nums), content=VALUES(content)"""
        params = (self['title'], self['create_date'], self['url'], self['url_obj_id'], self['front_img_url'],
                  self['front_img_path'], self['praise_nums'], self['fav_nums'],
                  self['comment_nums'], self['content'], self['tags'])
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
                            watch_user_num, click_num, crawl_time)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num),
                        comments_num=VALUES(comments_num), watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)"""
        zhuhu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = "".join(self["url"])
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_nums("".join(self["answer_num"]))
        comments_num = extract_nums("".join(self["comments_num"]))
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhuhu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num,
                            comments_num, create_time, update_time, crawl_time) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num),
                        praise_num=VALUES(praise_num), update_time=VALUES(update_time)"""
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (self["zhihu_id"], self["url"], self["question_id"], self["author_id"], self["content"],
                  self["praise_num"], self["comments_num"], create_time, update_time,
                  self["crawl_time"].strftime(SQL_DATETIME_FORMAT))

        return insert_sql, params
