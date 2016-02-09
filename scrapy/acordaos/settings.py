#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Scrapy settings for stf project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'acordaos'

ITEM_PIPELINES = {
    'acordaos.pipelines.InteiroTeorPipeline': 1,
    'acordaos.pipelines.MongoDBPipeline': 1
}


FILES_STORE = 'inteiros_teores'

SPIDER_MODULES = ['acordaos.spiders']
NEWSPIDER_MODULE = 'acordaos.spiders_dev'


DOWNLOAD_DELAY = 3


MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = "DJs"
MONGO_COLLECTION = "all"

# TODO change log level to INFO
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'log_test'
LOG_ENABLED = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'stf (+http://www.yourdomain.com)'

