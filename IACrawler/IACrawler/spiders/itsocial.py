# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class ItsocialSpider(scrapy.Spider):
    name = 'itsocial'
    allowed_domains = ['itsocial.fr']
    start_urls = ['http://itsocial.fr/']

    def parse(self, response):

        titles = response.xpath('//*[@class="vc_row wpb_row td-pb-row vc_custom_1514676062177"]/div/div/div/div/div/div/div/a/@title').extract()
        link = response.xpath('//*[@class="vc_row wpb_row td-pb-row vc_custom_1514676062177"]/div/div/div/div/div/div/div/a/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}