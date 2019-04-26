# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class MitreviewSpider(scrapy.Spider):
    name = 'MitReview'
    allowed_domains = ['https://www.technologyreview.com/the-download/']
    start_urls = ['https://www.technologyreview.com/the-download']

    def parse(self, response):

        titles = response.xpath('//*[@class="download__headline"]/text()').extract()
        link = response.xpath('//*[@class="read-more"]/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}