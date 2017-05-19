# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import re
import logging
import sqlite3 as lite
import pymongo
from google.cloud import datastore
from scrapy.exporters import JsonItemExporter
from scrapy.exceptions import DropItem

from wuxia.items import BookItem, ChapterItem

class IdPipeline(object):
    def process_item(self, item, spider):
        if item['id']:
            return item
        else:
            logging.error("Id is missing in %s" % item)
            raise DropItem("Missing ID in %s" % item)

class DuplicatedPipeline(object):

    def __init__(self):
        self.books_seen = set()
        self.chapters_seen = set()

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            if item['id'] in self.books_seen:
                logging.error("Duplicate book found: %s" % item)
                raise DropItem("Duplicate book found: %s" % item)
            else:
                self.books_seen.add(item['id'])
        elif isinstance(item, ChapterItem):
            if item['id'] in self.chapters_seen:
                logging.error("Duplicate chapter found: %s" % item)
                raise DropItem("Duplicate chapter found: %s" % item)
            else:
                self.chapters_seen.add(item['id'])
        return item

class BookNamePipeline(object):
    def process_item(self, item, spider):
        check_col_name = 'name'
        if isinstance(item,ChapterItem):
            check_col_name = 'parent_book_name'
        # If this is a book, the name should contain index, else drop it
        if "Index" in item[check_col_name] or "Table of Contents" in item[check_col_name] or "Sovereign of the Three Realms" in item[check_col_name]:
            # Get rid of (Chinese Name)
            item[check_col_name] = re.sub(r"\s*\(.+\)","",item[check_col_name])
            # Get rid of - Index
            item[check_col_name] = re.sub(r"\s*\W*\s*Index","",item[check_col_name])
            # Get rid of Table of Contents
            item[check_col_name] = re.sub(r"T\w+\s\w+\sC\w+","",item[check_col_name])
            # Get rid of -
            item[check_col_name] = re.sub(r"\s\W\s*","",item[check_col_name])
        else:
            logging.error("This is not a book, missing index in %s" % item)
            raise DropItem("This is not a book, missing index in %s" % item)
        return item

# Use this pipeline to get rid of teaser and glossary chapters
class ValidChapterPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, ChapterItem) and len('"""' + item['article_html'] + '"""') < 300:
            # Check article_html for length
            # Teaser only contains image
            raise DropItem("This is a teaser chapter in %s" % item)
        return item


class MongoPipeline(object):

    books_collection_name = 'books'
    chapters_collection_name = 'chapters'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGODB_URI'),
            mongo_db = crawler.settings.get('MONGODB_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.db[self.books_collection_name].create_index(["likes", pymongo.DESCENDING])
        self.db[self.chapters_collection_name].create_index(["parent_book_id", pymongo.ASCENDING])
        self.client.close()

    def process_item(self,item, spider):
        if isinstance(item, BookItem):
            self.db[self.books_collection_name].insert(dict(item))
        elif isinstance(item, ChapterItem):
            self.db[self.chapters_collection_name].insert(dict(item))
        return item

class GoogleDatastorePipeline(object):

    def __init__(self, datastore_id):
        self.datastore_id = datastore_id

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            datastore_id = crawler.settings.get('GDATASTORE_ID')
        )

    def open_spider(self, spider):
        self.client = datastore.Client(self.datastore_id)

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            key = self.client.key('Book', item['id'])
            book = datastore.Entity(key, exclude_from_indexes=['description','cover_url','id'])
            book.update(dict(item))
            self.client.put(book)
        if isinstance(item, ChapterItem):
            parent_key = self.client.key('Book', item['parent_book_id'])
            key = self.client.key('Chapter', item['id'], parent=parent_key)
            chapter = datastore.Entity(key, exclude_from_indexes=['id','article_html','article_footer'])
            chapter.update(dict(item))
            self.client.put(chapter)
