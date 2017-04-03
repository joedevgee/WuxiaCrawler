import scrapy
from scrapy.loader import ItemLoader
from wuxia.items import BookItem, ChapterItem

class WuxiaSpider(scrapy.Spider):

    name = 'Spider'

    allowed_domains = [
        'wuxiaworld.com',
    ]

    start_urls = [
        'http://www.wuxiaworld.com',
    ]

    def parse(self, response):
        for book in response.css('li.menu-item ul.sub-menu li.menu-item'):
            for book in book.css('a::attr(href)').extract():
                yield scrapy.Request(book, callback=self.parse_book)

    def parse_book(self, response):

        # Scrape the book item
        l = ItemLoader(item=BookItem(), response=response)
        l.add_xpath('id', '//link[@rel="shortlink"]/@href',re='p\D(\d+)')
        l.add_xpath('name', '//meta[@property="og:title"]/@content')
        l.add_xpath('description','//meta[@name="description"]/@content')
        l.add_xpath('published_time','//meta[@property="article:published_time"]/@content')
        l.add_xpath('modified_time','//meta[@property="article:modified_time"]/@content')
        yield l.load_item()

        # Scrape chapters link
        first_chapter = response.xpath('//a/@href').re_first(r'http.+\w+\Wchapter\W\d+')
        init_chapter_request = scrapy.Request(first_chapter,callback=self.parse_chapters)
        # Send book id for chapters as reference to parent book
        init_chapter_request.meta['book_id'] = response.xpath('//link[@rel="shortlink"]/@href').re_first('p\D(\d+)')
        init_chapter_request.meta['book_name'] = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        yield init_chapter_request
            
    def parse_chapters(self, response):
        l = ItemLoader(item=ChapterItem(), response=response)
        l.add_xpath('id', '//link[@rel="shortlink"]/@href',re='p\D(\d+)')
        l.add_xpath('name', '//meta[@property="og:title"]/@content')
        l.add_value('parent_book_id', response.meta['book_id'])
        l.add_value('parent_book_name', response.meta['book_name'])
        yield l.load_item()
    