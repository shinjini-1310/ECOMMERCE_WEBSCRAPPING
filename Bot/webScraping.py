'''
Please create 2 folders : AmazonProductData for storing the Excel file,
WebpageSnapshots for storing the full-screen screenshots per webpage visited by bot
'''

import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd

class webScrapper:

    def __init__(self,driver_path,product_name):

        self.product_name = product_name
        self.driver_path = driver_path

    def amzn_web_scrapper(self):

        prod_nm_split = self.product_name.strip().split(" ")
        prod_nm_url = "+".join(prod_nm_split)

        service_obj = Service(self.driver_path)
        my_options = webdriver.ChromeOptions()
        my_options.add_argument('--headless')
        my_options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=service_obj,options=my_options)
        url = 'https://www.amazon.in/s?k='+prod_nm_url
        driver.get(url)
        height = driver.execute_script('return document.documentElement.scrollHeight')
        width = driver.execute_script('return document.documentElement.scrollWidth')
        driver.set_window_size(width, height)

        wait = WebDriverWait(driver,10)

        try: wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '#a-page')))
        except: print("Timeout Exception: First webpage did not load within 10 seconds.")

        no_of_webpages = driver.find_elements(By.CSS_SELECTOR, '.s-pagination-item')
        webpage_num = []

        for page in no_of_webpages:
            if page.text in ['Previous', '...', 'Next']: pass
            else: webpage_num.append(page.text)

        if len(webpage_num) > 1: no_of_webpages = webpage_num[-1]
        else: no_of_webpages = webpage_num[0]

        webpage_no = 1
        product_title_list = []
        product_price_list = []

        print("TOTAL NO OF WEBPAGES TO SCRAP FOR THIS PRODUCT : ",no_of_webpages,"\n")

        while webpage_no<= int(no_of_webpages):

            print("****ANALYSING WEBPAGE NO ",str(webpage_no),"****\n")

            try: wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '#a-page')))
            except: print("Timeout Exception: Webpage did not load within 10 seconds.")

            driver.implicitly_wait(10)

            driver.save_screenshot('WebpageSnapshots/WebPageNo_'+str(webpage_no)+'.png')

            card_titles = driver.find_elements(By.CSS_SELECTOR, '.a-size-mini.a-spacing-none.a-color-base')
            card_prices = driver.find_elements(By.CSS_SELECTOR,'.a-price-whole')

            for title,price in zip(card_titles,card_prices):

                product_title_list.append(title.text)
                product_price_list.append(price.text)
                print("TITLE ------->",title.text)
                print("PRICE ------->Rs.",price.text,"\n")

            if webpage_no == int(no_of_webpages): break

            else:

                driver.find_element(By.LINK_TEXT, "Next").click()
                time.sleep(3)
                webpage_no+=1

        product_title_list = [title for title in product_title_list if title]
        product_price_list = [price for price in product_price_list if price]

        titles_df = pd.DataFrame(product_title_list)
        titles_df.columns = ["Product Name"]
        titles_df['Price'] = product_price_list
        titles_df.to_excel('AmazonProductData\\amzn_webscrapping.xlsx', sheet_name='Amazon Website Product Details', index=False)

        driver.close()

product_name = sys.argv[1]
obj = webScrapper('[full path for chromedriver.exe]',product_name)
obj.amzn_web_scrapper()