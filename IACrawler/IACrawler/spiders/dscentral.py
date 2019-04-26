# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class DscentralSpider(scrapy.Spider):
    name = 'dscentral'
    allowed_domains = ['https://www.datasciencecentral.com']
    start_urls = ['https://www.datasciencecentral.com/']

    def parse(self, response):

        titles = response.xpath('//*[@id="xg_layout_column_2"]/div[3]/div[2]/div/div[2]/h3/a/text()').extract()
        link = response.xpath('//*[@id="xg_layout_column_2"]/div[3]/div[2]/div/div[2]/h3/a/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}