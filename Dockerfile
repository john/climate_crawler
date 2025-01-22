# To use:
# docker build -t climate-crawler .
# docker build -t climate-crawler --build-arg CONTAINER_NAME="doe-crawl" --build-arg ALLOWED_DOMAINS="[\"www.energy.gov\"]" --build-arg START_URLS="[\"https://www.energy.gov/\"]" .

# Next iteratino this should pass in the values for CMD
# docker run climate-crawler

FROM python:3.9-slim

WORKDIR /app

COPY climate_crawler.py .

RUN pip install scrapy scrapy-fake-useragent azure-storage-blob

# TODO: pass in the start URLs and allowed domains as arguments
# CMD ["python", "-u", "general_crawler.py"]

# Options: doe, dot, etc. Originally doe-crawl, but the 'crawl' part seems unnecesary (but check before switching)
ARG CONTAINER_NAME
ARG ALLOWED_DOMAINS
ARG START_URLS

# ARG CONTAINER_NAME = "doe-crawl"
# ARG ALLOWED_DOMAINS = "[\"www.energy.gov\"]"
# ARG START_URLS = "[\"https://www.energy.gov/\"]"
#  "--start_urls", "[\"https://www.energy.gov/sitemap.xml\"]"] 

CMD ["python", "-u", "climate_crawler.py", \
     "--container_name", ${CONTAINER_NAME}, \
     "--allowed_domains", ${ALLOWED_DOMAINS}, \
     "--start_urls", ${START_URLS}]"]
