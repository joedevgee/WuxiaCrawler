import scrapy
from scrapy.loader import ItemLoader
from wuxia.items import BookItem

class WuxiaSpider(scrapy.Spider):

    name = 'Spider'

    start_urls = [
        'http://www.wuxiaworld.com',
    ]

    def parse(self, response):
        for book in response.css('li.menu-item ul.sub-menu li.menu-item'):
            for book in book.css('a::attr(href)').extract():
                yield scrapy.Request(book, callback=self.parse_book)

    def parse_book(self, response):
        l = ItemLoader(item=BookItem(), response=response)
        l.add_xpath('id', '//link[@rel="shortlink"]/@href',re='p\D(\d+)')
        l.add_xpath('name', '//meta[@property="og:title"]/@content')
        l.add_xpath('description','//meta[@name="description"]/@content')
        return l.load_item()

    # def parse_book(self, response):
    #     book_title = response.xpath('//meta[@property="og:title"]/@content').re(r'(.+)\s\W')
    #     book_abre = response.xpath('//a/@href').re_first(r'com\W(\w+)\W.+chapter')
    #     book_desc = response.xpath('//meta[@name="description"]/@content').extract_first()
    #     book_author = response.xpath
    #     if book_title is not None and book_abre != "legend":
    #         yield {
    #             'title': book_title,
    #             'abre': book_abre,
    #             'desc': book_desc,
    #         }
    #         first_chapter = response.xpath('//a[contains(@href, "-chapter-1/")]/@href').extract_first()
    #         yield scrapy.Request(first_chapter, callback=self.parse_chapters)
        
    def parse_chapters(self, response):
        ch_title = response.xpath('//meta[@itemprop="headline"]/@content').extract_first()
        ch_html = response.xpath('//div[@itemprop="articleBody"]').extract()
        yield {
            'article_title': ch_title,
            'article_content': ch_html,
        }
    