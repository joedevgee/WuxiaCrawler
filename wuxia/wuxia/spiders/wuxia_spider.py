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

        # Send book id for chapters as reference to parent book
        book_id = response.xpath('//link[@rel="shortlink"]/@href').re_first('p\D(\d+)')
        book_name = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        article_body = response.xpath('//div[@itemprop="articleBody"]')
        # Scrape chapters link
        for chapter_link in article_body.xpath('.//a/@href').extract(): # For test purpose, only get the first one
            yield self.follow_chapter_link(chapter_link,book_id,book_name)
            
    def parse_chapters(self, response):
        l = ItemLoader(item=ChapterItem(), response=response)
        l.add_xpath('id', '//link[@rel="shortlink"]/@href',re='p\D(\d+)')
        l.add_xpath('name', '//meta[@property="og:title"]/@content')
        l.add_value('parent_book_id', response.meta['book_id'])
        l.add_value('parent_book_name', response.meta['book_name'])
        article_body = response.xpath('//div[@itemprop="articleBody"]/p').extract()
        l.add_value('article_html',article_body)
        l.add_value('article_footer','<br>')
        l.add_xpath('article_footer','//div[@itemprop="articleBody"]/text()',re='\W\d+\W.+')
        yield l.load_item()

        book_id = response.meta['book_id']
        book_name = response.meta['book_name']

        # retrieve previous and next chapter links
        for chapter_link in response.xpath('//div[@itemprop="articleBody"]/p/a/@href').extract() + response.xpath('//div[@itemprop="articleBody"]/p/span/a/@href').extract():
            if chapter_link is not None:
                yield self.follow_chapter_link(chapter_link,book_id,book_name)

    def follow_chapter_link(self,url,book_id,book_name):
        new_request = scrapy.Request(url,callback=self.parse_chapters)
        new_request.meta['book_id'] = book_id
        new_request.meta['book_name'] = book_name
        return new_request