# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class ApproximatelycorrectSpider(scrapy.Spider):
    name = 'approximatelycorrect'
    allowed_domains = ['http://approximatelycorrect.com']
    start_urls = ['http://approximatelycorrect.com/']

    def parse(self, response):

        titles = response.xpath('//*[@class="entry-title"]/a/text()').extract()
        link = response.xpath('//*[@class="entry-title"]/a/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}
