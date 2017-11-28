# -*- coding: utf-8 -*-
__author__ = 'zx'
__date__ = '10/27/17 22:00'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "jobbole"])
execute(["scrapy", "crawl", "zhihu"])
# execute(["scrapy", "crawl", "lagou"])