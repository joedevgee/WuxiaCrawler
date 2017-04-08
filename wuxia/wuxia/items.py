# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

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

def replace_nav_header(value):
    # clean previous chapter and next chapter link
    head = value
    head = re.sub(r"\Wp\W.*Previous\sChapter.+Next\sChapter.+span\W\W\Wp\W","",head)
    return head

def replace_jump_footer(value):
    # clean contents inside <sup>...</sup>
    article = value
    article = re.sub(r"\Wsup.+onclick.+\W\Wsup\W","",article)
    return article

class ChapterItem(scrapy.Item):
    id = scrapy.Field(
        output_processor = TakeFirst(),
    )
    name = scrapy.Field(
        output_processor = TakeFirst(),
    )
    parent_book_id = scrapy.Field(
        output_processor = TakeFirst(),
    )
    parent_book_name = scrapy.Field(
        output_processor = TakeFirst(),
    )
    article_html = scrapy.Field(
        input_processor = MapCompose(replace_nav_header,replace_jump_footer),
        output_processor = Join(),
    )
    article_footer = scrapy.Field(
        output_processor = Join('<br>'),
    )
