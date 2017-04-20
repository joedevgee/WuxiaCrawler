# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import dateutil.parser
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags
from datetime import datetime

def string_to_datetime(value):
    # Time stemp is in this format: "2017-04-03T19:49:24+00:00"
    formatted_time = dateutil.parser.parse(value)
    return formatted_time

def string_to_int(value):
    # id field scraped from website is string, make it integer
    return int(value)

class BookItem(scrapy.Item):
    _id = scrapy.Field(
        input_processor = MapCompose(string_to_int),
        output_processor = TakeFirst(),
    )
    name = scrapy.Field(
        output_processor = TakeFirst(),
    )
    description = scrapy.Field(
        output_processor = TakeFirst(),
    )
    cover_url = scrapy.Field(
        output_processor = TakeFirst(),
    )
    likes = scrapy.Field(
        input_processor = MapCompose(string_to_int),
        output_processor = TakeFirst(),
    )
    published_time = scrapy.Field(
        input_processor = MapCompose(string_to_datetime),
        output_processor = TakeFirst(),
    )
    modified_time = scrapy.Field(
        input_processor = MapCompose(string_to_datetime),
        output_processor = TakeFirst(),
    )

def replace_nav_header(value):
    # clean previous chapter and next chapter link
    head = value
    head = re.sub(r"^\Wp\W.+Previous.+Next.+$","",head)
    return head

def replace_ch_title(value):
    # clan <p>Chapter 123</p> such
    title = value
    title = re.sub(r"\W\w*.+Chapter.*\d+.+$","",title)
    return title

def replace_jump_footer(value):
    # clean contents inside <sup>...</sup>
    article = value
    article = re.sub("\s*class.+\(\d+\)\W","",article)
    article = re.sub("\<\/a\>","",article)
    return article

def add_li_footer(value):
    # add <li>...</li>
    return '<li>'+value+'</li>'

class ChapterItem(scrapy.Item):
    _id = scrapy.Field(
        input_processor = MapCompose(string_to_int),
        output_processor = TakeFirst(),
    )
    name = scrapy.Field(
        output_processor = TakeFirst(),
    )
    parent_book_id = scrapy.Field(
        input_processor = MapCompose(string_to_int),
        output_processor = TakeFirst(),
    )
    parent_book_name = scrapy.Field(
        output_processor = TakeFirst(),
    )
    article_html = scrapy.Field(
        input_processor = MapCompose(replace_nav_header,replace_ch_title,replace_jump_footer),
        output_processor = Join(),
    )
    article_footer = scrapy.Field(
        input_processor = MapCompose(add_li_footer),
        output_processor = Join(),
    )
    published_time = scrapy.Field(
        input_processor = MapCompose(string_to_datetime),
        output_processor = TakeFirst(),
    )
    modified_time = scrapy.Field(
        input_processor = MapCompose(string_to_datetime),
        output_processor = TakeFirst(),
    )
