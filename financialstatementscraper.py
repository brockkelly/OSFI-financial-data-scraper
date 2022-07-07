import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd

# define number of months
months = 60

# define number of banks: total = 47 (9 Inactive)
banks = 31

# list of banks
banklist = ['Total All Banks', 'Total Domestic Banks', 'ADS Canadian Bank', 'B2B Bank', 'Bank of Montreal', 'The Bank of Nova Scotia', 'Canadian Imperial Bank of Commerce', 'Canadian Tire Bank', 'Canadian Western Bank',
 'Concentra Bank', 'CS Alterna Bank', 'Digital Commerce Bank', 'Duo Bank of Canada', 'Equitable Bank', 'Exchange Bank of Canada', 'First Nations Bank of Canada', 'General Bank of Canada',
     'Home Bank', 'HomeEquity Bank', 'Laurentian Bank of Canada', 'Manulife Bank of Canada', 'National Bank of Canada', "President's Choice Bank", 'RFA Bank of Canada', 'Rogers Bank', 'Royal Bank of Canada'
     , 'Tangerine Bank', 'The Toronto-Dominion Bank', 'Vancity Community Investment Bank',
        'VersaBank', 'Wealth One Bank of Canada']

path = '/Users/brockkelly/Desktop/Personal Projects/chromedriver'

options = Options()
options.add_argument('headless')
driver = webdriver.Chrome(path, chrome_options = options)


driver.get('https://www.osfi-bsif.gc.ca/Eng/wt-ow/Pages/FINDAT.aspx')
driver.implicitly_wait(5)

# switch to iframe
iframe = driver.find_element_by_xpath('//*[@id="ctl00_ctl61_g_69670f48_11c6_4626_9f60_e63007ee266c_FINDATIFrame"]')
driver.switch_to.frame(iframe)

# defining original window within selenium environment
original_window = driver.current_window_handle

# creating empty dataframe for assets and liabilities
assetsdf = []
liabilitiesdf = []

# bank button
bankdd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_institutionTypeCriteria_institutionsDropDownList"]')
bankbuttons = bankdd.find_elements_by_tag_name('option')

# for bank in bankbuttons:
#     banklist.append(bank.text)
# print(banklist)


j = -1
while j < (len(bankbuttons)-1):
    
    j +=1
    if bankbuttons[j].text not in banklist:
        continue  

    bankbuttons[j].click()

    #open dropdown menu for dates
    datedd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_monthlyDatesDropDownList"]')
    #driver.implicitly_wait(3)

    # need to loop over each of these
    buttons = datedd.find_elements_by_tag_name('option')
    # if len(buttons) < months:
    #     continue

    # submit button
    submit = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_submitButton"]')

    # loop over all dates
    i = 0
    while i < months:
        buttons[i].click()
        submit.click()
        
        # grab table of sports
        try:
            sports = WebDriverWait(driver, 5).until(
                EC.number_of_windows_to_be(2)
            )
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break 

            url = driver.current_url

            # pulling asset and liabilty tables
            df = pd.read_html(
                url, 
                attrs={'bordercolor': 'lightgrey'})

            assets = df[0]
            #assets = assets.drop(assets.columns[1], axis = 1)
            assets = assets.drop([0])
            assets.columns = ['item', 'foreign', 'total']

            liabilities = df[1]
            #liabilities = liabilities.drop(liabilities.columns[1], axis = 1)
            liabilities = liabilities.drop([0])
            liabilities.columns = ['item', 'foreign', 'total']

            # pulling current date and bank name data
            dfname = pd.read_html(
                url, 
                attrs={'border': '0'})

            dfname = dfname[0]
            bank = dfname.loc[0,0]

            date = dfname.loc[2,0]
            date = date.replace('As At ', '')
            date = date.replace('(in thousands of dollars)', '')

            # combining data frames
            assets['bank'] = bank
            assets['date'] = date
            assetsdf.append(assets)
            #pd.concat([assetsdf, assets])

            liabilities['bank'] = bank
            liabilities['date'] = date
            liabilitiesdf.append(liabilities)
            #pd.concat([liabilitiesdf, liabilities])

            
        except:
            driver.quit()

        # switch back to original window
        driver.switch_to.window(original_window)

        # switch to iframe
        iframe = driver.find_element_by_xpath('//*[@id="ctl00_ctl61_g_69670f48_11c6_4626_9f60_e63007ee266c_FINDATIFrame"]')
        driver.switch_to.frame(iframe)

        # bank button
        bankdd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_institutionTypeCriteria_institutionsDropDownList"]')
        bankbuttons = bankdd.find_elements_by_tag_name('option')        

        #open dropdown menu for dates
        datedd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_monthlyDatesDropDownList"]')
        datedd.click()
        #driver.implicitly_wait(3)

        # need to loop over each of these
        buttons = datedd.find_elements_by_tag_name('option')

        # submit button
        submit = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_submitButton"]')
        
        i += 1

assetsdf
totalassets = pd.concat(assetsdf)
totalassets.to_csv('totalassets.csv')
totalliabilities = pd.concat(liabilitiesdf)
totalliabilities.to_csv('totalliabilities.csv')





