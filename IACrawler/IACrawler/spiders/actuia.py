# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class ActuiaSpider(scrapy.Spider):
    name = 'actuia'
    allowed_domains = ['actuia.com']
    start_urls = ['http://actuia.com/']

    def parse(self, response):
        titles = response.xpath('//*[@id="td-outer-wrap"]/div[2]/div/div/div/div/div/div/div/h3/a/text()').extract()
        link = response.xpath('//*[@id="td-outer-wrap"]/div[2]/div/div/div/div/div/div/div/h3/a/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}
