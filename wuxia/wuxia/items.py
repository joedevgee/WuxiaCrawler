# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

class WuxiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BookItem(scrapy.Item):
    id = scrapy.Field(
        output_processor = TakeFirst(),
    )
    name = scrapy.Field(
        output_processor = TakeFirst(),
    )
    description = scrapy.Field(
        output_processor = TakeFirst(),
    )
    published_time = scrapy.Field(
        output_processor = TakeFirst(),
    )
    modified_time = scrapy.Field(
        output_processor = TakeFirst(),
    )

