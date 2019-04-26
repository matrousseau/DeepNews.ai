# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class KdnuggetsSpider(scrapy.Spider):
    name = 'kdnuggets'
    allowed_domains = ['https://www.kdnuggets.com']
    start_urls = ['https://www.kdnuggets.com/']

    def parse(self, response):

        titles = response.xpath('//*[@class="latn"]/tr/td/table/tr/td/ol/li/a/b/text()').extract()
        link = response.xpath('//*[@class="latn"]/tr/td/table/tr/td/ol/li/a/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}

