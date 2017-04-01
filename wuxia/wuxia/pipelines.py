# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import re
from scrapy.exceptions import DropItem
from wuxia.items import BookItem

class WuxiaPipeline(object):
    def process_item(self, item, spider):
        return item

class IdPipeline(object):
    def process_item(self, item, spider):
        if item['id']:
            return item
        else:
            raise DropItem("Missing ID in %s" % item)

class DuplicatedBookPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            if item['id'] in self.ids_seen:
                raise DropItem("Duplicate book found: %s" % item)
        return item

class BookNamePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            # If this is a book, the name should contain index, else drop it
            if "Index" in item['name']:
                # Get rid of (Chinese Name)
                item['name'] = re.sub(r"\s*\(.+\)","",item['name'])
                # Get rid of - Index
                item['name'] = re.sub(r"\s\W\sIndex","",item['name'])
            else:
                raise DropItem("This is not a book, missing index in %s" % item)
            # Clean book name, get rid of Chinese content and Index
        return item

