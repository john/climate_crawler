# connection_string = 'DefaultEndpointsProtocol=https;AccountName=climatecrawl;AccountKey=3XOvKRK53zUzDp9eTyYMCdje8NW495NPCKFLi9QI5bviSHzg8tE5rbXzwSy9Ve7jYWGhVg5Jx9g2+ASt7l/8wg==;EndpointSuffix=core.windows.net'

"""
This is a web crawling script using Scrapy framework to index the website https://www.globalchange.gov/
and save the raw HTML content to Azure Blob Storage.

TO USE
From the same directory as this script, run:
`docker build -t globalchange-crawler .`

Then
`docker run globalchange-crawler`

Alternatively you could set up docker compose, which would make it easier to
do this using a Docker volume, so visited_urls could be persisted across sessions.

You could also edit the Dockerfile to have ENTRYPOINT as the last line, comment out the running
of the script, then ssh into the container and run it directly from there.

To get the name of the crawler container:
`docker ps`

Now you can open a new terminal and run a shell in the container using the name you just got:
`docker exec -t -i {$name} /bin/bash`

inside the container you can run the scraper:
python -u globalchange_crawler.py
"""

import scrapy
from scrapy.crawler import CrawlerProcess
import time
from datetime import datetime
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
import gzip
import os
import logging

class GlobalchangeSpider(scrapy.Spider):
    name = "globalchange_spider"

    # -----------> Flipflop XML vs HTML
    # start_urls = ["https://www.globalchange.gov/"]
    start_urls = ["https://www.globalchange.gov/sitemap.xml"]
    
    allowed_domains = ["www.globalchange.gov"]
    visited_urls = set()

    custom_settings = {
        'ROBOTSTXT_OBEY': True  # Respect robots.txt rules
    }

    def __init__(self):
        self.load_visited_urls()
 
    def parse(self, response):
        # Save the visited URL
        self.logger.info(f"------------------------> Just got reponse from this url: {response.url}")
        self.visited_urls.add(response.url)

        #----------- this block compresses the page and sends it to Azure:
        # Compress HTML/XML content
        compressed_body = gzip.compress(response.body)

        # Save compressed HTML/XML to Azure Blob Storage
        connection_string = 'DefaultEndpointsProtocol=https;AccountName=climatecrawl;AccountKey=3XOvKRK53zUzDp9eTyYMCdje8NW495NPCKFLi9QI5bviSHzg8tE5rbXzwSy9Ve7jYWGhVg5Jx9g2+ASt7l/8wg==;EndpointSuffix=core.windows.net'
        container_name = 'globalchange-crawl'  # Specify the desired container name
        directory_name = datetime.now().strftime('%Y-%m-%d')  # Specify the desired directory name
        filename = response.url.split("/")[-1] + ".gz"
        blob_name = os.path.join(directory_name, filename)

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(compressed_body, overwrite=True)
        self.logger.info(f"Saved file {blob_name} to Azure Blob Storage")
        #----------- 

        

        # Parse the HTML/XML with Scrapy
        try:
            # -----------> Flipflop XML vs HTML
            # links = response.css('a::attr(href)').getall()
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            links = response.xpath('//ns:url/ns:loc/text()', namespaces=namespaces).getall()

        except:
            links = set()
            self.logger.info(f"Response content isn't text, probably a PDF")

        # output how many links were found
        self.logger.info(f"Found {len(links)} links")

        # Follow links and continue crawling
        for link in links:
            absolute_url = response.urljoin(link)
            parsed_url = urlparse(absolute_url)
            if (
                parsed_url.netloc == self.allowed_domains[0]
                and absolute_url not in self.visited_urls
                and "?f%" not in absolute_url
            ):
                self.logger.info(f"Fetching {absolute_url}")
                yield scrapy.Request(absolute_url, callback=self.parse)

    def closed(self, reason):
        self.save_visited_urls()

    def save_visited_urls(self):
        with open("visited_urls.txt", "w") as file:
            for url in self.visited_urls:
                file.write(url + "\n")

    def load_visited_urls(self):
        try:
            with open("visited_urls.txt", "r") as file:
                for line in file:
                    self.visited_urls.add(line.strip())
        except FileNotFoundError:
            pass

# Configure logging level to INFO
logging.getLogger("scrapy").setLevel(logging.INFO)

# Create a CrawlerProcess instance
process = CrawlerProcess(settings={
    'DOWNLOAD_DELAY': 1,  # Add a 1-second delay between requests
    'AUTOTHROTTLE_ENABLED': True,  # Enable autothrottle
    'AUTOTHROTTLE_START_DELAY': 1,  # Initial delay for autothrottle
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1,  # Maintain 1 request per second
    'AUTOTHROTTLE_DEBUG': False,  # Disable autothrottle debug mode
    'HTTPCACHE_ENABLED': True,  # Enable HTTP caching
    # -----------> Flipflop XML vs HTML
    # 'DEPTH_LIMIT': 0,
    'DEPTH_LIMIT': 1,
    'LOG_LEVEL': 'INFO',
})

# Configure settings and start the crawling process
process.crawl(GlobalchangeSpider)
process.start()
