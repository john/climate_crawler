# connection_string = 'DefaultEndpointsProtocol=https;AccountName=climatecrawl;AccountKey=3XOvKRK53zUzDp9eTyYMCdje8NW495NPCKFLi9QI5bviSHzg8tE5rbXzwSy9Ve7jYWGhVg5Jx9g2+ASt7l/8wg==;EndpointSuffix=core.windows.net'

"""
This is a web crawling script using Scrapy framework to index the website https://www.energy.gov/
and save the raw HTML content to Azure Blob Storage.

TO USE
From the same directory as this script, run:
`docker build -t doe-crawler .`

Then
`docker run doe-crawler`

Alternatively you could set up docker compose, which would make it easier to
do this using a Docker volume, so visited_urls could be persisted across sessions.

You could also edit the Dockerfile to have ENTRYPOINT as the last line, comment out the running
of the script, then ssh into the container and run it directly from there.

To get the name of the crawler container:
`docker ps`

Now you can open a new terminal and run a shell in the container using the name you just got:
`docker exec -t -i {$name} /bin/bash`

inside the container you can run the scraper:
python -u doe_crawler.py
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

class DoeSpider(scrapy.Spider):
    name = "doe_spider"

    # -----------> Flipflop XML vs HTML
    # start_urls = ["https://www.energy.gov/sitemap.xml", "https://www.energy.gov/"]
    start_urls = ["https://www.doe.gov/sitemap.xml?page=1", "https://www.doe.gov/sitemap.xml?page=2", "https://www.doe.gov/sitemap.xml?page=3", "https://www.doe.gov/sitemap.xml?page=4", "https://www.doe.gov/sitemap.xml?page=5", "https://www.doe.gov/sitemap.xml?page=6", "https://www.doe.gov/sitemap.xml?page=7", "https://www.doe.gov/sitemap.xml?page=8", "https://www.doe.gov/sitemap.xml?page=9", "https://www.doe.gov/sitemap.xml?page=10", "https://www.doe.gov/sitemap.xml?page=11", "https://www.doe.gov/sitemap.xml?page=12", "https://www.doe.gov/sitemap.xml?page=13", "https://www.doe.gov/sitemap.xml?page=14", "https://www.doe.gov/sitemap.xml?page=15", "https://www.doe.gov/sitemap.xml?page=16", "https://www.doe.gov/sitemap.xml?page=17", "https://www.doe.gov/sitemap.xml?page=18", "https://www.doe.gov/sitemap.xml?page=19", "https://www.doe.gov/sitemap.xml?page=20", "https://www.doe.gov/sitemap.xml?page=21", "https://www.doe.gov/sitemap.xml?page=22", "https://www.doe.gov/sitemap.xml?page=23", "https://www.doe.gov/sitemap.xml?page=24", "https://www.doe.gov/sitemap.xml?page=25", "https://www.doe.gov/sitemap.xml?page=26", "https://www.doe.gov/sitemap.xml?page=27", "https://www.doe.gov/sitemap.xml?page=28", "https://www.doe.gov/sitemap.xml?page=29", "https://www.doe.gov/sitemap.xml?page=30", "https://www.doe.gov/sitemap.xml?page=31", "https://www.doe.gov/sitemap.xml?page=32", "https://www.doe.gov/sitemap.xml?page=33", "https://www.doe.gov/sitemap.xml?page=34", "https://www.doe.gov/sitemap.xml?page=35", "https://www.doe.gov/sitemap.xml?page=36", "https://www.doe.gov/sitemap.xml?page=37", "https://www.doe.gov/sitemap.xml?page=38", "https://www.doe.gov/sitemap.xml?page=39", "https://www.doe.gov/sitemap.xml?page=40", "https://www.doe.gov/sitemap.xml?page=41", "https://www.doe.gov/sitemap.xml?page=42", "https://www.doe.gov/sitemap.xml?page=43", "https://www.doe.gov/sitemap.xml?page=44", "https://www.doe.gov/sitemap.xml?page=45", "https://www.doe.gov/sitemap.xml?page=46", "https://www.doe.gov/sitemap.xml?page=47", "https://www.doe.gov/sitemap.xml?page=48", "https://www.doe.gov/sitemap.xml?page=49"]
    
    allowed_domains = ["www.energy.gov"]
    visited_urls = set()

    custom_settings = {
        'ROBOTSTXT_OBEY': True  # Respect robots.txt rules
    }

    def __init__(self):
        self.load_visited_urls()
 
    def parse(self, response):
        # Save the visited URL
        self.visited_urls.add(response.url)

        # Compress HTML content
        compressed_body = gzip.compress(response.body)

        # Save compressed HTML to Azure Blob Storage
        connection_string = 'DefaultEndpointsProtocol=https;AccountName=climatecrawl;AccountKey=3XOvKRK53zUzDp9eTyYMCdje8NW495NPCKFLi9QI5bviSHzg8tE5rbXzwSy9Ve7jYWGhVg5Jx9g2+ASt7l/8wg==;EndpointSuffix=core.windows.net'
        # TODO: confirm container name
        container_name = 'doe-crawl'  # Specify the desired container name
        directory_name = directory_name = datetime.now().strftime('%Y-%m-%d')  # Specify the desired directory name
        filename = response.url.split("/")[-1] + ".gz"
        blob_name = os.path.join(directory_name, filename)

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(compressed_body, overwrite=True)

        self.logger.info(f"Saved file {blob_name} to Azure Blob Storage")

        # Parse the HTML with Scrapy
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
                # -----------> Flipflop XML vs HTML
                # and "?f%" not in absolute_url
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
    # 'DEPTH_LIMIT': 0, # for whole sites
    'DEPTH_LIMIT': 1, # for sitemaps
    'LOG_LEVEL': 'INFO',
})

# Configure settings and start the crawling process
process.crawl(DoeSpider)
process.start()
