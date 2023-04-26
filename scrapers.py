import datetime
import json
import os
from typing import List

import scrapy
from scrapy import Request
import pandas as pd
from scrapy.crawler import CrawlerProcess

from constants import DATA_PATH, CSV_PATH
from property import Property

if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)

if not os.path.exists(CSV_PATH):
    os.mkdir(CSV_PATH)


# start_urls = [
#     'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/grad/novi-sad/lista/po-stranici/10/',
#     'https://www.4zida.rs/prodaja-stanova/novi-sad'
# ]

class RealEstateSpider(scrapy.Spider):
    name = ""
    properties = []


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_urls()

    def create_urls(self) -> None:
        pass

    def closed(self, reason):
        if len(self.properties) > 0:
            date = datetime.datetime.now()
            df = pd.DataFrame.from_records([property.to_dict() for property in self.properties])
            df['date_scraped'] = date
            df.to_csv(os.path.join(CSV_PATH, f'{self.name}_properties_{date.strftime("%Y-%m-%d_%H-%M-%S")}.csv'), index=False)


class CetriZidaSpider(RealEstateSpider):
    name = "cetiri_zida"
    n_pages = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_urls()

    def create_urls(self) -> None:
        for page in range(1, self.n_pages):
            self.start_urls.append(f'https://www.4zida.rs/prodaja-stanova/novi-sad/?strana={page}/')

    def parse(self, response):
        for add in response.css('div.ed-card-details'):
            price = add.css('span.mb-2.block.text-2xl.font-medium::text').get()
            if price:
                price = price.replace('€', '').replace('.', '').strip()

            size = add.css('strong.text-base.ng-star-inserted::text').get()
            if size:
                size = size.replace('m²', '')

            street = add.css('div.font-medium span.mb-2.text-lg.uppercase::text').get()
            if street:
                street = street.strip()

            location = add.css('div.font-medium span.block.text-base::text').get()
            if location:
                location = location.split(',')[0].strip()
                if location == 'Gradske lokacije':
                    location = street

            title = add.css('h3.description::text').get()

            price_per_size = None
            if price and size:
                price_per_size = float(price)/float(size)

            self.properties.append(
                Property(title=title,
                         location=location,
                         street=street,
                         size=size,
                         price=price,
                         price_per_size=price_per_size,
                         date_published=datetime.datetime.now(),
                         under_construction=False
                         )
            )


class NekretnineRsSpider(RealEstateSpider):
    name = "nekretnine_rs"
    n_pages = 215

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_urls()

    def start_requests(self):
        for url in self.start_urls:

            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Host': 'www.nekretnine.rs',
                'Referer': 'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/grad/novi-sad/lista/po-stranici/10/',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
            }

            yield Request(url=url, headers=headers, callback=self.parse)

    def create_urls(self) -> None:
        for page in range(1, self.n_pages):
            self.start_urls.append(f'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/grad/novi-sad/lista/po-stranici/20/stranica/{page}/')

    def parse(self, response):
        for offer in response.css("div.offer-body"):
            title = offer.css("a::text").get()
            if title:
                title = title.replace('\n', '').strip()

            location = offer.css('p.offer-location::text').get()
            if location:
                location = location.replace('\n', '').strip().split(',')[0]

            try:
                street = title.split(',')[2].strip()
            except IndexError as e:
                street = ''

            if location:
                location = location.replace('\n', '').strip().split(',')[0]

                if location == 'Ribljja pijaca':
                    location = 'Riblja pijaca'

            date_published = offer.css('div.mt-1.mt-lg-2.mb-lg-0.d-md-block.offer-meta-info.offer-adress::text').get()
            if date_published:
                date_published = date_published.replace('\n', '').strip().split('|')[0].strip()
                date_published = datetime.datetime.strptime(date_published, '%d.%m.%Y')

            price = offer.css('p.offer-price span::text').get()
            if price:
                try:
                    price = float(price.replace('EUR', '').replace(' ', '').strip())
                except ValueError as e:
                    price = ''

            price_per_size = offer.css('p.offer-price small::text').get()
            if price_per_size:
                try:
                    price_per_size = float(price_per_size.replace('€/m²', '').replace(' ', '').strip())
                except ValueError as e:
                    price_per_size = None

            size = offer.css('p.offer-price.offer-price--invert span::text').get()
            if size:
                try:
                    size = float(size.replace('m²', '').replace(' ', '').strip())
                except ValueError as e:
                    size = None

            self.properties.append(
                Property(title=title,
                         location=location,
                         street=street,
                         size=size,
                         price=price,
                         price_per_size=price_per_size,
                         date_published=date_published,
                         under_construction=False
                         )
            )


class CityExpertSpider(RealEstateSpider):
    name = "city_expert"
    n_pages = 25

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_urls()

    def create_urls(self) -> None:
        for page in range(1, self.n_pages):
            self.start_urls.append('https://cityexpert.rs/api/Search?req={"cityId":2,"rentOrSale":"s",'
                                   '"currentPage":' + str(page) + ',"searchSource":"regular","sort":"datedsc"}')


    def parse(self, response):
        json_data = json.loads(response.body)
        for result in json_data['result']:
            try:
                self.properties.append(Property(title='',
                                                location=result['polygons'][-1],
                                                street=result['street'],
                                                size=result['size'],
                                                price=result['price'],
                                                price_per_size=result['pricePerSize'],
                                                date_published=result['firstPublished'],
                                                under_construction=result['underConstruction']))
            except Exception as e:
                print(e)


process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {"format": "json"},
    },
})

process.crawl(CetriZidaSpider)
process.start()
