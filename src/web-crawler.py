# from lxml import html
from bs4 import BeautifulSoup
import requests
import csv


class Crawler:
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.depth = None
        self.current_depth = 0
        self.depth_links = []
        self.offers = set()

    def crawl(self):
        self.get_links(self.starting_url, 2)

        # while self.current_depth < self.depth:
        #     current_links = []
        #     for link in self.depth_links[self.current_depth]:
        #         current_app = self.get_specials(link)
        #         current_links.extend(current_app.links)
        #         self.apps.append(current_app)
        #         time.sleep(5)
        #     self.current_depth += 1
        #     self.depth_links.append(current_links)

    def get_links(self, link, depth):

        start_page = requests.get(link).text
        start_soup = BeautifulSoup(start_page, 'html.parser')
        page = 1

        while page <= depth:
            specials_link = start_soup.find_all('a', class_='gutter_item')[10]['href'].split('snr')[0] + 'page=' + str(page)
            url = requests.get(specials_link).text
            specials_soup = BeautifulSoup(url, 'html.parser')

            for link in specials_soup.findAll('a', {'class': 'search_result_row'}):
                href = link.get('href').split('?')[0]
                self.get_data(href)
            page += 1

    def get_data(self, item_url):
        item_page = requests.get(item_url).text
        item_soup = BeautifulSoup(item_page, 'html.parser')

        with open('Sales.csv', 'w') as file:
            writer = csv.writer(file)
            headers = ['Game', 'Reviews', 'Discount', 'Price']
            writer.writerow(headers)

            for data in item_soup.find_all('div', {'class': 'responsive_page_content'}):
                item_name = data.find('div', {'class': 'apphub_AppName'})
                item_reviews = data.find('span', {'itemprop': 'description'})
                item_discount = data.find('div', {'class': 'discount_pct'})
                item_price = data.find('div', {'class': 'discount_final_price'})

            if item_name and item_reviews and item_discount and item_price is not None:
                game = Games(item_name.string, item_reviews.string, item_discount.string, item_price.string)
                writer.writerow([item_name.string, item_reviews.string, item_discount.string, item_price.string.replace(',', '.')])
                self.offers.add(game)


class Games:
    def __init__(self, name, user_reviews, discount, price):
        self.name = name.encode('utf-8')
        self.user_reviews = user_reviews.encode('utf-8')
        self.discount = discount.encode('utf-8')
        self.price = price.encode('utf-8')

    def __str__(self):
        return('Game: ' + self.name.decode('utf-8') + '\r\nUser reviews: ' + self.user_reviews.decode('utf-8') +
               '\r\nDiscount: ' + self.discount.decode('utf-8') + '\r\nPrice: ' + self.price.decode('utf-8') + '\r\n')


crawler = Crawler('https://store.steampowered.com')
crawler.crawl()

for app in crawler.offers:
    print(app)
