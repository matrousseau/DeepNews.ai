# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class MediumtechSpider(scrapy.Spider):
    name = 'mediumtech'
    allowed_domains = ['https://medium.com/topic/technology']
    start_urls = ['https://medium.com/topic/technology/']

    def parse(self, response):
        titles = response.xpath('//*[@id="root"]/div/section/section[1]/div[3]/div[1]/section/div/section/div[1]/div[1]/div[1]/h3/a/text()').extract()
        link = response.xpath('//*[@id="root"]/div/section/section[1]/div[3]/div[1]/section/div/section/div[1]/div[1]/div[1]/h3/a/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}
