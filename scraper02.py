from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from time import perf_counter

class StockTableScraper:
    symbol = []
    market_price = []
    book_value = []
    company_urls = []
    data = {}
    url = 'https://merolagani.com/LatestMarket.aspx'
    
    try:
        os.remove('table.txt')
    except FileNotFoundError as identifier:
        pass
    
    def fetch_html_text(self, url):
        response = requests.get(url)
        
        if response.status_code == 200:
            return response
        else:
            print("Page is not responding...")

    def parse_html_text(self, html):
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table", attrs={"class":"table table-hover live-trading sortable"})

        trows = table.find("tbody").find_all("tr")
        # trows = tbody.find_all("tr")

        for row in trows:
            company = row.find('td')
            self.symbol.append(company.text)
        
        self.create_company_urls(self.symbol)

    def create_company_urls(self, symbol):
        for company_name in self.symbol:
            company_url = 'https://merolagani.com/CompanyDetail.aspx?symbol=' + company_name
            # company_url = company_url + company_name
            self.company_urls.append(company_url)
        
        self.get_company_details(self.company_urls, symbol)


    def get_company_details(self, company_urls, company_name):
        for each_url in self.company_urls:
            response = self.fetch_html_text(each_url)
            soup = BeautifulSoup(response.content, 'lxml')
            table = soup.find('table', attrs={'class': 'table table-striped table-hover table-zeromargin'})

            mkt_price = table.find(id='ctl00_ContentPlaceHolder1_CompanyDetail1_lblMarketPrice')
            if mkt_price is not None:
                self.market_price.append(mkt_price.text.strip().replace(',', ''))
                bok_value = table.find_all('td')
                self.book_value.append(bok_value[11].text.strip().replace(',', ''))
            else:
                print("Element not found!")

        self.create_dataframe(company_name, self.market_price, self.book_value)
     
    def toText(self, symbol_table):
        fileObj = open('table.txt', 'a+', encoding='utf-8')
        fileObj.write(symbol_table)
        fileObj.write('\n')

    def create_dataframe(self, company_name, market_price, book_value):
        df = pd.DataFrame(list(zip(company_name, market_price, book_value)), columns=['symbol', 'marketPrice', 'bookValue'])
        df['marketPrice'] = df['marketPrice'].astype(float)
        df['bookValue'] = df['bookValue'].astype(float)
        df['diff'] = df['marketPrice'] - df['bookValue']
        print(df[(df['marketPrice']<=df['bookValue']+100) & df['bookValue'] != 0].sort_values(by='diff', ascending=False))

    def run(self):
        response = self.fetch_html_text(self.url)
        # print(response)
        self.parse_html_text(response.text)
        # self.toDataframe()


if __name__ == '__main__':
    t1_start = perf_counter()
    scraper = StockTableScraper().run()
    # scraper.run()
    t2_stop = perf_counter()

    print("-----------------------------------------")

    print("Time diff: {0}".format(t2_stop - t1_start))