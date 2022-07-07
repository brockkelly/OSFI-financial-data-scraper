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
banklist = ['Total All Banks', 'Total Domestic Banks', 'Bank of Montreal', 'The Bank of Nova Scotia', 'Canadian Imperial Bank of Commerce', 'Canadian Western Bank',
 'Concentra Bank', 'CS Alterna Bank', 'Equitable Bank', 'First Nations Bank of Canada',
     'Home Bank', 'HomeEquity Bank', 'Laurentian Bank of Canada', 'Manulife Bank of Canada', 'National Bank of Canada', 'RFA Bank of Canada', 'Royal Bank of Canada'
     , 'Tangerine Bank', 'The Toronto-Dominion Bank',
        'VersaBank', 'Wealth One Bank of Canada']

path = '/Users/brockkelly/Desktop/Personal Projects/chromedriver'

options = Options()
#options.add_argument('headless')

driver = webdriver.Chrome(path, chrome_options = options)
driver.get('https://www.osfi-bsif.gc.ca/Eng/wt-ow/Pages/FINDAT.aspx')
driver.implicitly_wait(5)

# switch to iframe
iframe = driver.find_element_by_xpath('//*[@id="ctl00_ctl61_g_69670f48_11c6_4626_9f60_e63007ee266c_FINDATIFrame"]')
driver.switch_to.frame(iframe)

# defining original window within selenium environment
original_window = driver.current_window_handle

# creating empty dataframe for assets and liabilities
capitaldf = []

# click on quarterly data button
driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyRadioButton"]').click()

# click on dropdown button for BCAR capital components
capitaldropdown = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyDropDownList"]')
capitaldropdown.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyDropDownList"]/option[3]').click()

# bank button
bankdd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_institutionTypeCriteria_institutionsDropDownList"]')
bankbuttons = bankdd.find_elements_by_tag_name('option')

# for bank in bankbuttons:
#     banklist.append(bank.text)
# print(banklist)

j = -1
while j < (5):
    
    j +=1
    if bankbuttons[j].text not in banklist:
        continue

    bankbuttons[j].click()

    #open dropdown menu for dates
    datedd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyPeriodsDropDownList"]')
    #driver.implicitly_wait(3)

    # need to loop over each of these
    buttons = datedd.find_elements_by_tag_name('option')
    # if len(buttons) < months:
    #     continue

    # submit button
    submit = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_submitButton"]')

    # loop over all dates
    i = 0
    while i < 3:
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

                # pulling capital tables
                df = pd.read_html(
                    url, 
                    attrs={'border': '1'})

                capital = df[0]
                capital.columns = ['item', 'amount']

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
                capital['bank'] = bank
                capital['date'] = date
                capitaldf.append(capital)

        except:
            driver.quit()
        

        # switch to original window
        driver.switch_to.window(original_window)

        # switch to iframe
        iframe = driver.find_element_by_xpath('//*[@id="ctl00_ctl61_g_69670f48_11c6_4626_9f60_e63007ee266c_FINDATIFrame"]')
        driver.switch_to.frame(iframe)

        # click on quarterly data button
        driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyRadioButton"]').click()

        # # click on dropdown button for BCAR capital components
        capitaldropdown = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyDropDownList"]')
        capitaldropdown.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyDropDownList"]/option[3]').click()

        # bank button
        bankdd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_institutionTypeCriteria_institutionsDropDownList"]')
        bankbuttons = bankdd.find_elements_by_tag_name('option')        

        #open dropdown menu for dates
        datedd = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_dtiReportCriteria_quarterlyPeriodsDropDownList"]')
        datedd.click()
        #driver.implicitly_wait(3)

        # need to loop over each of these
        buttons = datedd.find_elements_by_tag_name('option')

        # submit button
        submit = driver.find_element_by_xpath('//*[@id="DTIWebPartManager_gwpDTIBankControl1_DTIBankControl1_submitButton"]')
        
        i += 1


totalcapital = pd.concat(capitaldf)
totalcapital.to_csv('totalcapital.csv')

totalcapital
capitaldf