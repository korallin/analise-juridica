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

FILES_STORE = 'inteiros_teores'

SPIDER_MODULES = ['acordaos.spiders']
NEWSPIDER_MODULE = 'acordaos.spiders_dev'

DOWNLOAD_HANDLERS = {'s3': None}

DOWNLOAD_DELAY = 2


MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = "DJs"

# TODO change log level to INFO
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'decisao.log'
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'

# http://programmers.stackexchange.com/questions/91760/how-to-be-a-good-citizen-when-crawling-web-sites
# https://webscraping.com/blog/How-to-crawl-websites-without-being-blocked/
# Depois criar minha página e explicar porque não sou uma ameaça
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

