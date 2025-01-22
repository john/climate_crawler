# Climate Crawlers
Some crawlers in Python for crawling and archiving government climate and energy sites. This was an experiment in pair programming with ChatGPT, it's crude, a separate crawler needs to be written for each site, and each crawler has only been run once.
A valuable future project would set up a permanent archive with the ability to easily add new target sites, and which would allow repeat archiving, so that changes over time could be tracked.

## Running
Each crawler is a Python script to do the crawling using the [Scrapy framework](https://scrapy.org/), and a Dockerfile to create a container in which the crawler can run. It starts from apex domains, and can also accept sitemap.xml URLs

To crawl any site you first build the container: `docker build -t climate-crawler .`

Then run it, passing in arguments specific to the site you want crawled. This is for the DOE:
```
docker build -t climate-crawler \
  --build-arg CONTAINER_NAME="doe-crawler" \
  --build-arg ALLOWED_DOMAINS="[\"www.energy.gov\"]" \
  --build-arg START_URLS="[\"https://www.energy.gov/\"]" \
```

Change the build-args for different sites:

### CARB
```
--build-arg CONTAINER_NAME="carb-crawler" \
--build-arg ALLOWED_DOMAINS="[\"ww2.arb.ca.gov\"]" \
--build-arg START_URLS="[\"https://ww2.arb.ca.gov/sitemap.xml?page=1\", \"https://ww2.arb.ca.gov/sitemap.xml?page=2\"]" \
```

### ClimateTRACE
```
allowed_domains = ['climatetrace.org']
start_urls = ['https://climatetrace.org/']
```

### DOT
```
start_urls = ["https://www.transportation.gov/sitemap.xml?page=1", "https://www.transportation.gov/sitemap.xml?page=2", "https://www.transportation.gov/sitemap.xml?page=3", "https://www.transportation.gov/sitemap.xml?page=4", "https://www.transportation.gov/sitemap.xml?page=5", "https://www.transportation.gov/sitemap.xml?page=6", "https://www.transportation.gov/sitemap.xml?page=7"]
allowed_domains = ["www.transportation.gov"]
```

### EPA
```
start_urls = ["https://www.epa.gov/sitemap.xml?page=1", "https://www.epa.gov/sitemap.xml?page=2", "https://www.epa.gov/sitemap.xml?page=3", "https://www.epa.gov/sitemap.xml?page=4", "https://www.epa.gov/sitemap.xml?page=5", "https://www.epa.gov/sitemap.xml?page=6", "https://www.epa.gov/sitemap.xml?page=7", "https://www.epa.gov/sitemap.xml?page=8", "https://www.epa.gov/sitemap.xml?page=9", "https://www.epa.gov/sitemap.xml?page=10", "https://www.epa.gov/sitemap.xml?page=11", "https://www.epa.gov/sitemap.xml?page=12", "https://www.epa.gov/sitemap.xml?page=13", "https://www.epa.gov/sitemap.xml?page=14", "https://www.epa.gov/sitemap.xml?page=15", "https://www.epa.gov/sitemap.xml?page=16", "https://www.epa.gov/sitemap.xml?page=17", "https://www.epa.gov/sitemap.xml?page=18", "https://www.epa.gov/sitemap.xml?page=19", "https://www.epa.gov/sitemap.xml?page=20", "https://www.epa.gov/sitemap.xml?page=21", "https://www.epa.gov/sitemap.xml?page=22", "https://www.epa.gov/sitemap.xml?page=23", "https://www.epa.gov/sitemap.xml?page=24", "https://www.epa.gov/sitemap.xml?page=25", "https://www.epa.gov/sitemap.xml?page=26", "https://www.epa.gov/sitemap.xml?page=27", "https://www.epa.gov/sitemap.xml?page=28", "https://www.epa.gov/sitemap.xml?page=29", "https://www.epa.gov/sitemap.xml?page=30", "https://www.epa.gov/sitemap.xml?page=31", "https://www.epa.gov/sitemap.xml?page=32", "https://www.epa.gov/sitemap.xml?page=33", "https://www.epa.gov/sitemap.xml?page=34", "https://www.epa.gov/sitemap.xml?page=35", "https://www.epa.gov/sitemap.xml?page=36", "https://www.epa.gov/sitemap.xml?page=37", "https://www.epa.gov/sitemap.xml?page=38", "https://www.epa.gov/sitemap.xml?page=39"]
allowed_domains = ["www.epa.gov"]
```

### Global Change
```
start_urls = ["https://www.globalchange.gov/sitemap.xml"]
allowed_domains = ["www.globalchange.gov"]
```

### NOAA
```
# start_urls = ["https://www.noaa.gov/sitemap.xml", "https://www.noaa.gov/"]
start_urls = ["https://www.noaa.gov/sitemap.xml"]
allowed_domains = ["www.noaa.gov"]
```

## Sites to add
- [Energy Information Agency](https://www.eia.gov/)
- [NASA](https://www.nasa.gov/)
- [Climate.gov](https://www.climate.gov/) (run by NOAA, but independent site)
- [DOI] (https://www.doi.gov/)
- [FERC](https://www.ferc.gov/)
- [USDA Climate Hubs](https://www.climatehubs.usda.gov/)
- [Energy Communities IWG](https://energycommunities.gov/)
- [USAID Climate](https://www.usaid.gov/climate)
- [Federal Geospatial Platform](https://www.geoplatform.gov/)
- [NAIC](https://content.naic.org/)
- [National Climate Task Force](https://www.whitehouse.gov/climate/) (Biden administration)
- [Office of the Chief Sustainability Officer](https://www.sustainability.gov/) (Biden administration)
- [American Climate Corp](https://www.acc.gov/) (Biden administration)
- [GSA Climate and Energy](https://www.gsa.gov/climate-action-and-sustainability)
- [Department of State Climate and COP sites](https://www.state.gov/policy-issues/climate-crisis/) (Biden administration)

## TODO
- Generalize, so there's a single generic crawler, to which you pass URLs
- Make it unnecessary to handle xml and html differently. maybe pass in a "format" var?
- Add timestamp to directory name
- Some kind of batching or pagination so it doesn't get all the URLs first, or so that it does the fetching per page batch, if possible
- Productioninze code: tests, CI/CD, etc
- Add an admin webapp to add URLs to crawl, to trigger crawls, to schedule them, and to link to the location of archived crawls
