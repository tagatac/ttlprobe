# -*- coding: utf-8 -*-
import scrapy


class AlexaSpider(scrapy.Spider):
    name = "alexa"
    allowed_domains = ["alexa.com"]
    start_urls = (
        'http://www.alexa.com/',
    )

    def parse(self, response):
        pass
