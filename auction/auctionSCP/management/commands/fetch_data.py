from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import time

from auctionSCP.models import Lot, LotPrice

class Command(BaseCommand):
    help = 'Fetches data the from websites'

    # URL Sources
    urls_source = '/home/manish/Apps/python/auction/auction/links.csv'

    # Selenium Configuration
    page_load_wait = 0.5 # Seconds
    chromedriver_path = '/home/manish/Apps/python/auction/auction/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=options)

    def handle(self, *args, **options):
        # Delete all existing data
        Lot.objects.all().delete()
        LotPrice.objects.all().delete()

        # Get List of URL from the CSV File
        with open(self.urls_source) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for i, row in enumerate(readCSV, 1):
                if i == 1:
                    url = row[0]
                    # Run URL in browser
                    self.browser.get(url)
                    # Wait for Page Load
                    time.sleep(self.page_load_wait)
                    # Scroll down to Get All Data
                    self.scrollAndLoad()
                    # Retrieve the Page
                    page_content = self.browser.page_source
                    # Create BeautifulSoup Instance
                    soup = BeautifulSoup(page_content, 'html.parser')
                    # Parse Content - Antiquorum
                    if 'antiquorum' in url:
                        source = 'antiquorum'
                        products = soup.find('div', {'id': 'products'}).find_all('div', {'class', 'shadow mt-4'})
                        # Initiating Atomic Transaction
                        with transaction.atomic():
                            for j, product in enumerate(products, 1):
                                if 1 == 1:
                                    lot = Lot()
                                    lot.url = url
                                    lot.source = source
                                    lot.auction_title = product.find_all('div', {'class': 'ml-auto p-2 bd-highlight'})[0].text
                                    lot.lot_number = product.find_all('h4')[0].text
                                    try:
                                        lot.name = product.find('span', {'itemprop': 'name'})['content']
                                    except:
                                        print('Ignoring %s - No Data' % lot.lot_number)
                                        continue

                                    lot.description = product.find('span', {'itemprop': 'description'})['content']
                                    lot.image_url = product.find('span', {'itemprop': 'image'})['content']
                                    lot.details_url = product.find_all('a')[2]['href']
                                    lot.grading = product.find('div', {'class': 'N_lots_grading col'}).text.replace('Grading System: ', '').strip()
                                    
                                    print("Working on: %s" % lot.lot_number)

                                    # Attributes
                                    attributes = product.find('div', {'class': 'N_lots_auction_title'}).find_all('p')
                                    for attribute in attributes:
                                        label = attribute.find('strong').text.strip()
                                        value = attribute.text.replace(label, '').strip().replace("'",'\\"')
                                        label_clean = label.lower().replace(' ', '_').replace('.','').strip()
                                        exec("lot.%s = '%s'" % (label_clean, value))

                                    # Sales Price - for Sold Lots
                                    sold_text = product.find_next_sibling('div', {'class': 'row'}).text.strip()
                                    if len(sold_text) > 0:
                                        lot.is_sold = True
                                        lot.sold_currency = sold_text[6:9]
                                        lot.sold_price = self.parseDecimal(sold_text[10:])
                                    else:
                                        lot.is_sold = False

                                    lot.save()

                                    # Estimated Price
                                    prices = product.find_all('p', {'class': 'N_lots_estimation'})
                                    for price in prices:
                                        price_text = price.text
                                        lot_price = LotPrice()
                                        lot_price.lot = lot
                                        lot_price.currency = price_text[0:4]
                                        lot_price.min_price = self.parseDecimal(price_text[4:].split('-')[0].strip())
                                        lot_price.max_price = self.parseDecimal(price_text[4:].split('-')[1].strip())
                                        lot_price.save()
    

        # Close Selenium Browser
        self.browser.quit()
        self.stdout.write(self.style.SUCCESS('Done!'))
    

    """ Scroll untill the data in page is completely loaded """
    def scrollAndLoad(self):
        SCROLL_PAUSE_TIME = 0.5

        # Get scroll height
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load content
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    """ Parses Decimal from String """
    def parseDecimal(self, text):
        return float(text.replace(',',''))