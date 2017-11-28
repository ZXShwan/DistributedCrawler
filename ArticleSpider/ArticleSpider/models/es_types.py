# -*- coding: utf-8 -*-
__author__ = 'zx'
__date__ = '11/27/17 18:48'

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Integer, Boolean, analyzer, InnerObjectWrapper, Completion, Text, Keyword
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class ArticleType(DocType):
    """
    bole article types
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


if __name__ == '__main__':
    ArticleType.init()