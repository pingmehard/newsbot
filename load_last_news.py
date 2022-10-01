from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import hashlib
from bs4 import BeautifulSoup as BS
from ddl import log_errors

def get_last_news_rbc():

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(".\chromedriver\chromedriver.exe", options=options)

    rbc = 'https://www.rbc.ru/short_news/'

    try:
        driver.set_page_load_timeout(6)
        driver.set_window_size(1920, 1080)
        driver.get(rbc)
    except:
        driver.execute_script("window.stop();")

    feed = BS(driver.page_source, 'lxml')

    news_link = feed.find('a', class_ = 'item__link')['href']
    news_title = feed.find('span', class_ = 'item__title').text.strip()


    driver_page = webdriver.Chrome(".\chromedriver\chromedriver.exe", options=options)
    
    try:
        driver_page.set_page_load_timeout(6)
        driver_page.set_window_size(1920, 1080)
        driver_page.get(news_link)
    except:
        driver_page.execute_script("window.stop();")

    site = BS(driver_page.page_source, 'lxml')
    try:
        try:
            news_text = site.find('div', class_ = 'article__text__main').text
        except Exception as e:
            log_errors(e)
            news_text = "\n".join([text.text for text in site.find_all('p')])
    except Exception as e:
        log_errors((e))
        news_text = '-'

    news_hash = hashlib.md5(news_link.encode()).hexdigest()

    driver.close()
    driver_page.close()

    where_from = 'rbc'

    return where_from, news_hash, news_link, news_title, news_text

def get_last_news_lenta():
    
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(".\chromedriver\chromedriver.exe", options=options)

    lenta = 'https://lenta.ru/parts/news/'
    lenta_short = 'https://lenta.ru'

    driver.get(lenta)
    feed = BS(driver.page_source, 'lxml')

    item = feed.find('ul', class_ = 'parts-page__body').find('a', class_ = 'card-full-news')

    # save links from news page
    if 'http' not in item['href']:
        link_page = lenta_short + item['href']
        news_link = lenta_short + item['href']
    else:
        link_page = item['href']
        news_link = item['href']

    news_hash = hashlib.md5(news_link.encode()).hexdigest()    

    # save news titles
    news_title = item.find('h3').text

    # save text from news
    try:
        driver_page = webdriver.Chrome(".\chromedriver\chromedriver.exe", options=options)
        driver_page.get(link_page)
        site = BS(driver_page.page_source, 'lxml')

        if 'moslenta' in item['href']:
            news_text = site.find('div', class_ = 'text').text
        else:
            news_text = site.find('div', class_ = 'topic-body').text
    except:
        news_text = '-'

    driver.close()
    driver_page.close()

    where_from = 'lenta'

    return where_from, news_hash, news_link, news_title, news_text

def get_last_news_ria():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path = r".\chromedriver\chromedriver.exe", options=options)

    site_link = 'https://ria.ru'

    driver.get(site_link)
    feed = BS(driver.page_source, 'lxml')

    try:
        item = feed.find('div', class_ = 'lenta__wrapper').find('a', class_ = 'lenta__item-size')
    except:
        item = feed.find('div', class_ = 'lenta__wrapper').find('a')

    # save links from news page
    link_page = site_link + item['href']
    news_link = link_page

    news_hash = hashlib.md5(news_link.encode()).hexdigest()    

    # save news titles
    news_title = item.find('span', class_ = 'lenta__item-text').text

    # save text from news
    try:
        driver_page = webdriver.Chrome(".\chromedriver\chromedriver.exe", options=options)
        driver_page.get(link_page)
        site = BS(driver_page.page_source, 'lxml')

        news_text = "\n".join([i.text for i in site.find('div', class_ = 'article__body').find_all('div', attrs={'data-type': ['text']})])

    except:
        news_text = '-'

    driver.close()
    driver_page.close()

    where_from = 'ria'

    return where_from, news_hash, news_link, news_title, news_text

def get_last_news_habr():

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path = r".\chromedriver\chromedriver.exe", options=options)

    site_link = 'https://habr.com'

    driver.get(site_link)
    feed = BS(driver.page_source, 'lxml')

    try:
        item = feed.find('section', id = 'news_block_1').find('a', class_ = 'tm-news-block-item__title')
    except:
        item = feed.find('section', id = 'news_block_1').find('a')

    # save links from news page
    link_page = site_link + item['href']
    news_link = link_page

    news_hash = hashlib.md5(news_link.encode()).hexdigest()    

    # save news titles
    news_title = item.text

    # save text from news
    try:
        driver_page = webdriver.Chrome(".\chromedriver\chromedriver.exe", options=options)
        driver_page.get(link_page)
        site = BS(driver_page.page_source, 'lxml')

        news_text = site.find('div', class_ = 'article-formatted-body').text

    except:
        news_text = '-'

    driver.close()
    driver_page.close()

    where_from = 'habr'

    return where_from, news_hash, news_link, news_title, news_text