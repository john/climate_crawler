# Climate Crawlers
Some crawlers in Python for crawling and archiving government climate and energy sites. This was an experiment in pair programming with ChatGPT, it's crude, a separate crawler needs to be written for each site, and each crawler has only been run once.
A valuable future project would set up a permanent archive with the ability to easily add new target sites, and which would allow repeat archiving, so that changes over time could be tracked.

## Running
Each crawler is a Python script to do the crawling using the [Scrapy framework](https://scrapy.org/), and a Dockerfile to create a container in which the crawler can run. It starts from apex domains, and can also accept sitemap.xml URLs

## Sites crawled
- CARB (ww2.arb.ca.gov)
- DOE (www.energy.gov)
- DOT (www.transportation.gov)
- EPA (www.epa.gov)
- Global Change (www.globalchange.gov)
- NOAA (noaa.gov)

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
- Productioninze code: tests, CI/CD, etc
- Add an admin webapp to add URLs to crawl, to trigger crawls, to schedule them, and to link to the location of archived crawls
