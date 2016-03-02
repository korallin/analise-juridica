#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import scrapy

from scrapy.exceptions import DropItem
import logging
from scrapy.pipelines.files import FilesPipeline


class MongoDBPipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if ('files' not in item) and ('file_urls' not in item):
            for data in item:
                if not data:
                    raise DropItem("Missing {0} in:\n{1}!".format(data, item))

        self.db[self.collection_name].insert(dict(item))
        return item


class InteiroTeorPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        for data in item:
            if not data:
                raise DropItem("Missing {0} in:\n{1}!".format(data, item))

        for file_url in item['file_urls']:
            yield scrapy.Request(file_url)

    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if file_paths:
            item['files'] = file_paths[0]
            del item['file_urls']
        else:
            logging.warning("Acordao {} nao possui inteiro teor!".format(item['acordaoId']))

        return item
