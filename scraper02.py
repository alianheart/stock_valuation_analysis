from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import os

class WikiTableScraper:
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
    


    def fetch(self, url):
        return requests.get(url)


    def parse(self, html):
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table", attrs={"class":"table table-hover live-trading sortable"})
        # thead = table.find("thead")
        # header = thead.find("th")
        # self.symbol.append(header.text)

        tbody = table.find("tbody")
        trows = tbody.find_all("tr")

        for row in trows:
            company = row.find('td')
            self.symbol.append(company.text)
        
        self.toCompanyLink(self.symbol)

    def toCompanyLink(self, symbol):  
        for company_name in self.symbol:
            company_url = 'https://merolagani.com/CompanyDetail.aspx?symbol='
            company_url = company_url + company_name
            self.company_urls.append(company_url)
        
        self.parseCompany(self.company_urls, symbol)


    def parseCompany(self, company_urls, company_name):
        for each_url in self.company_urls:
            response = self.fetch(each_url)
            soup = BeautifulSoup(response.content, 'lxml')
            table = soup.find('table', attrs={'class': 'table table-striped table-hover table-zeromargin'})

            mkt_price = table.find(id='ctl00_ContentPlaceHolder1_CompanyDetail1_lblMarketPrice')
            self.market_price.append(mkt_price.text.strip().replace(',', ''))

            bok_value = table.find_all('td')
            self.book_value.append(bok_value[11].text.strip().replace(',', ''))

        self.toDataframe(company_name, self.market_price, self.book_value)
            
        # print(self.market_price)
        # print('-' * 100)
        # print(self.book_value)
     

    def toText(self, symbol_table):
        fileObj = open('table.txt', 'a+', encoding='utf-8')
        fileObj.write(symbol_table)
        fileObj.write('\n')


    def toDataframe(self, company_name, market_price, book_value):
        df = pd.DataFrame(list(zip(company_name, market_price, book_value)), columns=['symbol', 'marketPrice', 'bookValue'])
        df['marketPrice'] = df['marketPrice'].astype(float)
        df['bookValue'] = df['bookValue'].astype(float)
        print(df[(df['marketPrice']<=df['bookValue']+40) & df['bookValue'] != 0])
        # print(df)


    def run(self):
        response = self.fetch(self.url)
        # print(response)
        self.parse(response.text)
        # self.toDataframe()


if __name__ == '__main__':
    scraper = WikiTableScraper()
    scraper.run()