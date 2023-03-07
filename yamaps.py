from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from datetime import date


def collect_data(url):
    delay = 3
    feeds, names, places, rates, towns_excel, dates = [], [], [], [], [], []
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--remote-debugging-port=9241")
    chromeOptions.binary_location = "/usr/bin/chromium-browser"
    service = Service()
    service.start()
    driver = webdriver.Remote(service.service_url, options=chromeOptions)
    time.sleep(3.5)
    driver.get(url)
    with open('/home/user/snap/maps/towns.txt', 'r', encoding='UTF-8') as file:
        towns = [i.strip() for i in file.readlines()]
    xpath1 = '/html/body/div[1]/div[2]/div[2]/header/div/div/div/form/div[2]/div/span/span/input'
    xpath2 = '/html/body/div[1]/div[2]/div[2]/header/div/div/div/form/div[1]/div/span/span/input'
    xpath3 = '/html/body/div[1]/div[2]/div[1]/header/div/div/div/form/div[1]/div/span/span/input'
    try:
        WebDriverWait(driver, delay).until(ec.presence_of_element_located((By.CLASS_NAME, 'home-panel-content-view__header-text')))
    except TimeoutException:
        time.sleep(delay)
    your_town = driver.find_element(By.CLASS_NAME, 'home-panel-content-view__header-text').text.strip()
    for town in towns:
        text = f'{town} ремонт телефонов'
        try:
            WebDriverWait(driver, delay).until(ec.presence_of_element_located((By.XPATH, xpath1)))
        except TimeoutException:
            time.sleep(delay)
        try:
            driver.find_element(By.XPATH, xpath1).send_keys(text)
        except NoSuchElementException:
            try:
                driver.find_element(By.XPATH, xpath2).send_keys(text)
            except NoSuchElementException:
                driver.find_element(By.XPATH, xpath3).send_keys(text)
        try:
            driver.find_element(By.XPATH, xpath1).send_keys(Keys.ENTER)
        except NoSuchElementException:
            try:
                driver.find_element(By.XPATH, xpath2).send_keys(Keys.ENTER)
            except NoSuchElementException:
                driver.find_element(By.XPATH, xpath3).send_keys(Keys.ENTER)
        try:
            WebDriverWait(driver, delay).until(ec.presence_of_element_located((By.CLASS_NAME, 'search-list-view__list')))
        except TimeoutException:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            try:
                address = soup.find('div', class_='business-contacts-view__address-link').text
            except AttributeError:
                print(town)
                continue
            if your_town == town:
                pass
            elif town not in address:
                driver.find_element(By.XPATH,
                                    '/html/body/div[1]/div[2]/div[1]/header/div/div/div/form/div[4]/button/span/div').click()
                print(town)
                continue
            name = soup.find('a', class_='card-title-view__title-link').text
            rating = soup.find('div', class_='business-card-title-view__header')
            try:
                rate = rating.find('span', class_='business-rating-badge-view__rating-text _size_m').text
            except AttributeError:
                rate = 0
            try:
                feed = rating.find('span', class_='business-header-rating-view__text _clickable').text
            except AttributeError:
                feed = 0
            if feed == 'Написать отзыв':
                feed = 0
                rate = 0
            if feed == '':
                feed = rating.find('span', class_='business-header-rating-view__text').text
            towns_excel.append(town)
            names.append(name.strip())
            places.append(address.strip())
            rates.append(rate)
            if feed != 0:
                feed = int(feed.split()[0])
            feeds.append(feed)
            dates.append(str(date.today()))
            driver.find_element(By.XPATH,
                                '/html/body/div[1]/div[2]/div[1]/header/div/div/div/form/div[4]/button/span/div').click()
            continue
        driver.find_element(By.CLASS_NAME, 'search-snippet-view__link-overlay').send_keys(Keys.END)
        time.sleep(0.5)
        src = driver.find_element(By.CLASS_NAME, 'search-list-view__list').get_attribute('innerHTML')
        soup = BeautifulSoup(src, 'lxml')
        k = 0
        for item in soup.find_all('div', class_='search-business-snippet-view__content'):
            try:
                address = item.find('div', class_='search-business-snippet-view__address').text
            except AttributeError:
                print(town)
                continue
            if your_town == town:
                pass
            elif town not in address:
                break
            name = item.find('div', class_='search-business-snippet-view__head').text
            rating = item.find('div', class_='search-business-snippet-view__rating-and-awards')
            try:
                rate = rating.find('span', class_='business-rating-badge-view__rating-text _size_m').text
            except AttributeError:
                rate = 0
            try:
                feed = rating.find('span', class_='business-rating-amount-view').text
            except AttributeError:
                feed = 0
            names.append(name.strip())
            places.append(address.strip())
            rates.append(rate)
            if feed != 0:
                feed = int(feed.split()[0])
            feeds.append(feed)
            dates.append(str(date.today()))
            k += 1
            if k == 12:
                break
        if k != 0:
            towns_excel.append(town)
            for i in range(k-1):
                towns_excel.append('')
        driver.find_element(By.XPATH,
                            '/html/body/div[1]/div[2]/div[1]/header/div/div/div/form/div[4]/button/span/div').click()
    driver.close()
    df = pd.DataFrame({'Город': towns_excel,
                       'Название': names,
                       'Адрес': places,
                       'Оценка': rates,
                       'Кол-во отзывов': feeds,
                       'Дата': dates})
    df.to_excel('/home/user/snap/maps/yamaps.xlsx', index=False)


def main():
    collect_data('https://www.yandex.ru/maps')


if __name__ == '__main__':
    main()
