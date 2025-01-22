# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

"""
python3 -u climate_trace_crawler.py
"""

import scrapy
from scrapy.crawler import CrawlerProcess
import gzip
import os

class ClimateTraceCrawler(scrapy.Spider):
    name = 'climate_trace'
    allowed_domains = ['climatetrace.org']
    start_urls = ['https://climatetrace.org/']

    def parse(self, response):
        # Create the directory if it doesn't exist
        directory = 'climate_trace_pages'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Get the page content
        content = response.body

        # Extract filename from URL
        url_components = response.url.split('/')
        filename = url_components[-1] if url_components[-1] else 'index'
        filename += '.html.gz'

        # Save the content to a gzip file
        with gzip.open(os.path.join(directory, filename), 'wb') as f:
            f.write(content)
        self.log('Saved file %s' % filename)

        # Follow all links on the page
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, callback=self.parse)
