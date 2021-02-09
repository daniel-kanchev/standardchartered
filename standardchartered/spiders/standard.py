import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from standardchartered.items import Article


class StandardSpider(scrapy.Spider):
    name = 'standard'
    start_urls = ['https://www.sc.com/en/insights/collections/']

    def parse(self, response):
        links = response.xpath('//div[@class="collection-column"]//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_collection)

    def parse_collection(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_pages = response.xpath('//nav[@class="prev-next-press-releases '
                                    'insight-topic-pagination"]//a/@href').getall()
        if next_pages:
            yield from response.follow_all(next_pages, self.parse_collection)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = response.xpath('//div[@class="entry-date updated published"]//text()').get().strip()
        date = datetime.strptime(date, '%d %B %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@class="fl-row-content-wrap"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        author = response.xpath('//span[@class="vcard author"]//text()').getall()
        author = [text for text in author if text.strip()]
        author = "\n".join(author).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)

        return item.load_item()
