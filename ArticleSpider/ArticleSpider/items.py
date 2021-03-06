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
from utils.common import extract_nums
from settings import SQL_DATE_FORMAT, SQL_DATETIME_FORMAT
from w3lib.html import remove_tags
from models.es_types import ArticleType, ZhihuAnswerType, ZhihuQuestionType, LagouType
from elasticsearch_dsl.connections import connections

es = connections.create_connection(ArticleType._doc_type.using)


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


def gen_suggests(index, info):
    """
    根据字符串生成搜索建议数组
    :param index:
    :param info:
    :return:
    """
    used_words = set()
    suggests = []

    for text, weight in info:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests



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
        params = (
            self['title'], self['create_date'], self['url'], self['url_obj_id'], self['front_img_url'],
            self['front_img_path'], self['praise_nums'], self['fav_nums'],
            self['comment_nums'], self['content'], self['tags']
        )
        return insert_sql, params

    def save_to_es(self):
        article = ArticleType()

        article.url = self['url']
        article.meta.id = self['url_obj_id']
        article.front_img_url = self['front_img_url']
        if 'front_img_path' in self:
            article.front_img_path = self['front_img_path']
        article.title = self['title']
        article.create_date = self['create_date']
        article.praise_nums = self['praise_nums']
        article.fav_nums = self['fav_nums']
        article.comment_nums = self['comment_nums']
        article.content = remove_tags(self['content'])
        article.tags = self['tags']

        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)))

        article.save()
        return


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
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num),
              comments_num=VALUES(comments_num), watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
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
        params = (
            zhuhu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time
        )

        return insert_sql, params

    def save_to_es(self):
        question = ZhihuQuestionType()

        question.zhihu_id = self['zhihu_id'][0]
        question.topics = ",".join(self["topics"])
        question.url = "".join(self["url"])
        question.title = "".join(self["title"])
        question.content = remove_tags("".join(self["content"]))
        question.answer_num = extract_nums("".join(self["answer_num"]))
        question.comments_num = extract_nums("".join(self["comments_num"]))
        if len(self["watch_user_num"]) == 2:
            question.watch_user_num = int(self["watch_user_num"][0])
            question.click_num = int(self["watch_user_num"][1])
        else:
            question.watch_user_num = int(self["watch_user_num"][0])
            question.click_num = 0
        question.crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        question.save()
        return


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
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num,
              comments_num, create_time, update_time, crawl_time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num),
              praise_num=VALUES(praise_num), update_time=VALUES(update_time)
        """
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"], self["author_id"], self["content"],
            self["praise_num"], self["comments_num"], create_time, update_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql, params

    def save_to_es(self):
        answer = ZhihuAnswerType()

        answer.zhihu_id = self['zhihu_id']
        answer.url = self['url']
        answer.question_id = self['question_id']
        answer.author_id = self['author_id']
        answer.content = remove_tags(self['content'])
        answer.praise_num = self['praise_num']
        answer.comments_num = self['comments_num']
        answer.create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        answer.update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        answer.crawl_time = self["crawl_time"].strftime(SQL_DATETIME_FORMAT)

        answer.save()
        return


def remove_slash(value):
    return value.replace("/", "")


def get_pub_time(value):
    return str(value).split()[0]


def handle_jobaddr(value):
    addr_list = str(value).split("\n")
    addr_list = [addr.strip() for addr in addr_list if addr.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    url = scrapy.Field()
    url_obj_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(input_processor=MapCompose(remove_slash))
    work_years = scrapy.Field(input_processor=MapCompose(remove_slash))
    degree = scrapy.Field(input_processor=MapCompose(remove_slash))
    job_type = scrapy.Field()
    publish_time = scrapy.Field(input_processor=MapCompose(get_pub_time))
    tags = scrapy.Field(input_processor=Join(","))
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(input_processor=MapCompose(remove_tags, handle_jobaddr))
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(url, url_obj_id, title, salary, job_city, work_years, degree, job_type, publish_time,
              tags, job_advantage, job_desc, job_addr, company_url, company_name, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc),
              work_years=VALUES(work_years), crawl_time=VALUES(crawl_time)
        """
        params = (
            self["url"], self["url_obj_id"], self["title"], self["salary"], self["job_city"], self["work_years"],
            self["degree"], self["job_type"], self["publish_time"], self["tags"], self["job_advantage"],
            self["job_desc"], self["job_addr"], self["company_url"], self["company_name"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        )
        return insert_sql, params

    def save_to_es(self):
        lagou = LagouType()

        lagou.url = self['url']
        lagou.meta.id = self['url_obj_id']
        lagou.title = self['title']
        lagou.salary = self['salary']
        lagou.job_city = remove_slash(self['job_city'])
        lagou.work_years = remove_slash(self['work_years'])
        lagou.degree = remove_slash(self['degree'])
        lagou.job_type = self['job_type']
        lagou.publish_time = get_pub_time(self['publish_time'])
        lagou.tags = self['tags']
        lagou.job_advantage = self['job_advantage']
        job_desc = remove_tags(self['job_desc'])
        lagou.job_desc = job_desc
        lagou.job_addr = handle_jobaddr(remove_tags(self['job_addr']))
        lagou.company_url = self['company_url']
        lagou.company_name = self['company_name']
        lagou.crawl_time = self["crawl_time"].strftime(SQL_DATETIME_FORMAT)

        lagou.save()
        return
