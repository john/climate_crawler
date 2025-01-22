# connection_string = 'DefaultEndpointsProtocol=https;AccountName=climatecrawl;AccountKey=3XOvKRK53zUzDp9eTyYMCdje8NW495NPCKFLi9QI5bviSHzg8tE5rbXzwSy9Ve7jYWGhVg5Jx9g2+ASt7l/8wg==;EndpointSuffix=core.windows.net'

"""
This is a web crawling script using Scrapy framework to index websites
and save the raw HTML content to Azure Blob Storage. Its main purpose is to
archive federal climate and energy data.

TO USE
From the same directory as this script, run:
```
docker build -t climate-crawler \
  --build-arg CONTAINER_NAME="doe-crawler" \
  --build-arg ALLOWED_DOMAINS="[\"www.energy.gov\"]" \
  --build-arg START_URLS="[\"https://www.energy.gov/\"]" \
```

```
docker build -t climate-crawler \
  --build-arg CONTAINER_NAME="globalchange-crawler" \
  --build-arg ALLOWED_DOMAINS="[\"https://www.globalchange.gov/\"]" \
  --build-arg START_URLS="[\"https://www.globalchange.gov/\"]" \
```

Then
`docker run climate-crawler`


For NREL:
docker build -t climate-crawler \
  --build-arg CONTAINER_NAME="nrel-crawler" \
  --build-arg ALLOWED_DOMAINS="[\"nrel.gov\", \"www.nrel.gov\"]" \
  --build-arg START_URLS="[\"https://www.nrel.gov/\"]" \


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
import scrapy-fake-useragent
import time
from datetime import datetime
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
import gzip
import os
import argparse
import json
import logging


class ClimateSpider(scrapy.Spider):
    name = "climate_spider"

    # TODO: get start_urls and allowed_domains from passed-in value or environment variable
    # -----------> Flipflop XML vs HTML
    # start_urls = ["https://www.energy.gov/sitemap.xml", "https://www.energy.gov/"]
    # start_urls = ["https://www.doe.gov/sitemap.xml?page=1", "https://www.doe.gov/sitemap.xml?page=2", "https://www.doe.gov/sitemap.xml?page=3", "https://www.doe.gov/sitemap.xml?page=4", "https://www.doe.gov/sitemap.xml?page=5", "https://www.doe.gov/sitemap.xml?page=6", "https://www.doe.gov/sitemap.xml?page=7", "https://www.doe.gov/sitemap.xml?page=8", "https://www.doe.gov/sitemap.xml?page=9", "https://www.doe.gov/sitemap.xml?page=10", "https://www.doe.gov/sitemap.xml?page=11", "https://www.doe.gov/sitemap.xml?page=12", "https://www.doe.gov/sitemap.xml?page=13", "https://www.doe.gov/sitemap.xml?page=14", "https://www.doe.gov/sitemap.xml?page=15", "https://www.doe.gov/sitemap.xml?page=16", "https://www.doe.gov/sitemap.xml?page=17", "https://www.doe.gov/sitemap.xml?page=18", "https://www.doe.gov/sitemap.xml?page=19", "https://www.doe.gov/sitemap.xml?page=20", "https://www.doe.gov/sitemap.xml?page=21", "https://www.doe.gov/sitemap.xml?page=22", "https://www.doe.gov/sitemap.xml?page=23", "https://www.doe.gov/sitemap.xml?page=24", "https://www.doe.gov/sitemap.xml?page=25", "https://www.doe.gov/sitemap.xml?page=26", "https://www.doe.gov/sitemap.xml?page=27", "https://www.doe.gov/sitemap.xml?page=28", "https://www.doe.gov/sitemap.xml?page=29", "https://www.doe.gov/sitemap.xml?page=30", "https://www.doe.gov/sitemap.xml?page=31", "https://www.doe.gov/sitemap.xml?page=32", "https://www.doe.gov/sitemap.xml?page=33", "https://www.doe.gov/sitemap.xml?page=34", "https://www.doe.gov/sitemap.xml?page=35", "https://www.doe.gov/sitemap.xml?page=36", "https://www.doe.gov/sitemap.xml?page=37", "https://www.doe.gov/sitemap.xml?page=38", "https://www.doe.gov/sitemap.xml?page=39", "https://www.doe.gov/sitemap.xml?page=40", "https://www.doe.gov/sitemap.xml?page=41", "https://www.doe.gov/sitemap.xml?page=42", "https://www.doe.gov/sitemap.xml?page=43", "https://www.doe.gov/sitemap.xml?page=44", "https://www.doe.gov/sitemap.xml?page=45", "https://www.doe.gov/sitemap.xml?page=46", "https://www.doe.gov/sitemap.xml?page=47", "https://www.doe.gov/sitemap.xml?page=48", "https://www.doe.gov/sitemap.xml?page=49"]
    # allowed_domains = ["www.energy.gov"]

    custom_settings = {
        'ROBOTSTXT_OBEY': True  # Respect robots.txt rules
    }

    def __init__(self, start_urls, allowed_domains, container_name, *args, **kwargs):
        super(ClimateSpider, self).__init__(*args, **kwargs)

        print(f"init: Allowed domains: {allowed_domains}")
        print(f"init: start_urls: {start_urls}")
        print(f"init: container_name: {container_name}")

        self.start_urls = start_urls
        self.allowed_domains = allowed_domains
        self.container_name = container_name
        self.visited_urls = set()
        self.load_visited_urls()
 
    def parse(self, response):

        # Compress HTML content
        compressed_body = gzip.compress(response.body)

        # Save compressed HTML to Azure Blob Storage
        connection_string = 'DefaultEndpointsProtocol=https;AccountName=climatecrawl;AccountKey=3XOvKRK53zUzDp9eTyYMCdje8NW495NPCKFLi9QI5bviSHzg8tE5rbXzwSy9Ve7jYWGhVg5Jx9g2+ASt7l/8wg==;EndpointSuffix=core.windows.net'
        
        # TODO: get container name from passed-in value or environment variable
        # container_name = 'doe-crawl'  # Specify the desired container name
        directory_name = directory_name = datetime.now().strftime('%Y-%m-%d')  # Create a date-based directory
        filename = response.url.split("/")[-1] + ".gz"

        blob_name = os.path.join(directory_name, filename)
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(compressed_body, overwrite=True)

        # Save the visited URL
        self.visited_urls.add(response.url)
        # self.logger.warning(f"Saved file {blob_name} to Azure Blob Storage")
        print(f"Saved file {blob_name} to Azure Blob Storage")

        # Parse the HTML with Scrapy
        try:
            # -----------> Flipflop XML vs HTML
            # html
            links = response.css('a::attr(href)').getall()

            # xml
            # namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            # links = response.xpath('//ns:url/ns:loc/text()', namespaces=namespaces).getall()

        except:
            links = set()
            print(f"Response content isn't text, probably a PDF")

        # self.logger.info(f"Found {len(links)} links")
        print(f"Found {len(links)} links")

        # Follow links and continue crawling
        for link in links:
            absolute_url = response.urljoin(link)
            parsed_url = urlparse(absolute_url)
            if (
                parsed_url.netloc == self.allowed_domains[0]
                and absolute_url not in self.visited_urls

                # I think this is just for html in one site? doe? I think it had some huge number of pages we didn't want with this in the url
                # and "?f%" not in absolute_url
            ):
                print(f"Fetching {absolute_url}")
                yield scrapy.Request(absolute_url, callback=self.parse)

    def closed(self, reason):
        self.save_visited_urls()

    # TODO: This should get returned to the caller, and/or saved to the Blob, since
    #       the container it's currently in will be destroyed when the spider is done.
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



# Parse command-line arguments
parser = argparse.ArgumentParser(description="DOE Crawler Script")
parser.add_argument(
    "--allowed_domains",
    type=str,
    required=True,
    help="Allowed domains for the crawler, provided as a JSON string (e.g., '[\"www.energy.gov\"]')."
)
parser.add_argument(
    "--start_urls",
    type=str,
    required=True,
    help="Start URLs for the crawler, provided as a JSON string (e.g., '[\"https://example.com\"]')."
)
parser.add_argument(
    "--container_name",
    type=str,
    required=True,
    help="The Azure Blob Storage container name for storing crawled data."
)

# Parse the arguments
args = parser.parse_args()

try:
    allowed_domains = json.loads(args.allowed_domains)
    start_urls = json.loads(args.start_urls)
    container_name = args.container_name
except json.JSONDecodeError as e:
    raise ValueError("Invalid JSON format in one of the arguments.") from e

print(f"Allowed domains: {allowed_domains}")
print(f"start_urls: {start_urls}")
print(f"container_name: {container_name}")

logging.getLogger("scrapy").setLevel(logging.WARNING)

# Create a CrawlerProcess instance
process = CrawlerProcess(settings={
    'DOWNLOAD_DELAY': 1,  # Add a 1-second delay between requests
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 1,
    'AUTOTHROTTLE_MAX_DELAY': 10,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1,  # Maintain 1 request per second
    'AUTOTHROTTLE_DEBUG': False,
    'HTTPCACHE_ENABLED': True,
    'LOG_LEVEL': 'WARNING',
    'COOKIES_ENABLED': True,
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    },
    'FAKEUSERAGENT_PROVIDERS': { 
        'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
        'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
        'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
    },
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    # Set DEPTH_LIMIT based on the type of crawling
    # DEPTH_LIMIT = 0 for crawling entire sites (e.g., HTML pages).
    # DEPTH_LIMIT = 1 for restricted crawls like sitemap exploration.
    'DEPTH_LIMIT': 30, # Set the maximum depth for crawling to something high but not insane. Keeping it truly unlimited can lead to infinite loops.
})


# Configure settings and start the crawling process
process.crawl(ClimateSpider, start_urls=start_urls, allowed_domains=allowed_domains, container_name=container_name)
process.start()
