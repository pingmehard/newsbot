from selenium import webdriver

from bs4 import BeautifulSoup as BS

def load_rbc():
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome("C:\chromedriver\chromedriver.exe")
    
    rbc = 'https://trends.rbc.ru/trends/short_news'
    link = []
    title = []
    text = []
    
    driver.get(rbc)
    feed = BS(driver.page_source, 'lxml')
    
    for item in feed.find('div', class_ = 'l-base__flex__content').find_all('div', class_ = 'item__title'):
        
        # save links from news page
        link.append(item.find('a')['href'])
        
        # save text from news
        driver_page = webdriver.Chrome("C:\chromedriver\chromedriver.exe")
        driver_page.get(item.find('a')['href'])
        site = BS(driver_page.page_source, 'lxml')
        try:
            text.append(site.find('div', class_ = 'article__text__main').text)
        except:
            text.append(site.find('div', class_ = 'article__text').text)
        finally:
            text.append('-')

        # save news titles
        title.append(item.text.strip())

    where_from = 'rbc'
        
    return where_from, title, link, text

def load_lenta():

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome("C:\chromedriver\chromedriver.exe")

    lenta = 'https://lenta.ru/parts/news/'
    lenta_short = 'https://lenta.ru'

    link = []
    title = []
    text = []

    driver.get(lenta)
    feed = BS(driver.page_source, 'lxml')

    for item in feed.find('ul', class_ = 'parts-page__body').find_all('a', class_ = 'card-full-news'):

        # save links from news page
        if 'http' not in item['href']:
            link_page = lenta_short + item['href']
            link.append(lenta_short + item['href'])
        else:
            link_page = item['href']
            link.append(item['href'])
        
        # save news titles
        title.append(item.find('h3').text)
        
        # save text from news
        try:
            driver_page = webdriver.Chrome("C:\chromedriver\chromedriver.exe")
            driver_page.get(link_page)
            site = BS(driver_page.page_source, 'lxml')

            if 'moslenta' in item['href']:
                text.append(site.find('div', class_ = 'text').text)
            else:
                text.append(site.find('div', class_ = 'topic-body').text)
        except:
            text.append('-')

    where_from = 'lenta' 
        
    return where_from, title, link, text