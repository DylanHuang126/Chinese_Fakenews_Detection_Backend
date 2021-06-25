from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import requests


userId = 'realtw'
Related_users_list = []
def Related_users(userId):
    browser = webdriver.Chrome('/Users/billhuang/NTU/senior1/專題/system/chromedriver')
    browser.get('https://www.ianalyseur.org')
    input_search = browser.find_element_by_class_name('form-control')
    #input_search.clear
    input_search.send_keys(userId)
    browser.find_element_by_class_name('btn-default').click()
    browser.find_element_by_link_text('關聯圖').click()
    ele_list = browser.find_elements_by_class_name('right')
    for ele in ele_list:
        Related_users_list.append(ele.get_attribute('class'))