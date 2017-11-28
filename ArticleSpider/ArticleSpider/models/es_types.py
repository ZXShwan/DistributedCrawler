# -*- coding: utf-8 -*-
__author__ = 'zx'
__date__ = '11/27/17 18:48'

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Integer, Boolean, analyzer, InnerObjectWrapper, Completion, Text, Keyword
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class ArticleType(DocType):
    """
    bole article types of es
    """
    url = Keyword()
    url_obj_id = Keyword()
    front_img_url = Keyword()
    front_img_path = Keyword()
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    praise_nums = Integer()
    fav_nums = Integer()
    comment_nums = Integer()
    content = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")

    class Meta:
        index = "jobbole"
        doc_type = "article"


class ZhihuQuestionType(DocType):
    """
    zhihu question types of es
    """
    zhihu_id = Keyword()
    topics = Text(analyzer="ik_max_word")
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    answer_num = Integer()
    comments_num = Integer()
    watch_user_num = Integer()
    click_num = Integer()
    crawl_time = Date()

    class Meta:
        index = "zhihu"
        doc_type = "question"


class ZhihuAnswerType(DocType):
    """
    zhihu answer types of es
    """
    zhihu_id = Keyword()
    url = Keyword()
    question_id = Keyword()
    author_id = Keyword()
    content = Text(analyzer="ik_max_word")
    praise_num = Integer()
    comments_num = Integer()
    create_time = Date()
    update_time = Date()
    crawl_time = Date()

    class Meta:
        index = "zhihu"
        doc_type = "answer"


class LagouType(DocType):
    """
    lagou types of es
    """
    url = Keyword()
    url_obj_id = Keyword()
    title = Text(analyzer="ik_max_word")
    salary = Integer()
    job_city = Keyword()
    work_years = Text()
    degree = Text(analyzer="ik_max_word")
    job_type = Text(analyzer="ik_max_word")
    publish_time = Text()
    tags = Text(analyzer="ik_max_word")
    job_advantage = Text(analyzer="ik_max_word")
    job_desc = Text(analyzer="ik_max_word")
    job_addr = Text(analyzer="ik_max_word")
    company_url = Keyword()
    company_name = Keyword()
    crawl_time = Date()

    class Meta:
        index = "lagou"
        doc_type = "jobs"


if __name__ == '__main__':
    ArticleType.init()
    ZhihuQuestionType.init()
    ZhihuAnswerType.init()
    LagouType.init()
