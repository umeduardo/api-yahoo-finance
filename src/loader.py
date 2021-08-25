from typing import Dict, List
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

import os
import time 
import pandas as pd
import platform

class Loader():
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    implicitly_wait: int = 5
    sleep_wait: int = 10
    finance_url: str = 'https://finance.yahoo.com/screener/new'

    browser: Chrome

    def __init__(self):
        self.__start_browser()


    def __get_executable_path(self) -> str:
        system_name: str = platform.platform().lower()
        if system_name.startswith('darwin'):
            return self.dir_path+'/../bin/chromedriver'
        elif system_name.startswith('linux'):
            return self.dir_path+'/../bin/chromedriver_linux'
        else:
            return self.dir_path+'/../bin/chromedriver.exe'

    
    def __start_browser(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless") 

        self.browser = webdriver.Chrome(executable_path=self.__get_executable_path(), options=chrome_options)
        self.browser.implicitly_wait(self.implicitly_wait)
        

    def process_data(self, dataframe: pd.DataFrame) -> Dict:
        """
        return a formatted {dataframe} inserting symbol as key
        """
        records: Dict = {}
        for index, row in dataframe.iterrows():
            records[row['symbol']] = {
                "symbol": row['symbol'],
                "name": row['name'],
                "price": f"{row['price']:.2f}",
            }
        return records



    def load_all_regions(self) -> List:
        """
        Return a list of regions availables
        eg:
        ["Brazil", "Peru", "Chile",...]
        """
        self.browser.get(self.finance_url)
        wait = WebDriverWait(self.browser, 10)

        #open dropdown with all regions
        btn_open_dropdown = self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[5]/div/div/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/ul/li/div/div')
        btn_open_dropdown.click()

        regions = self.browser.find_elements(By.XPATH, f'//*[@id="dropdown-menu"]//span')

        results: List = []
        for region in regions:
            results.append(region.get_attribute('innerHTML'))

        return results
        

    def load_stocks_from_region(self, region: str) -> Dict:
        """
        Return a dataset containing all results from {{region}}
        eg:
        {
            "AMX.BA": {
                "symbol": "AMX.BA",
                "name": "América Móvil, S.A.B. de C.V.",
                "price": "2089.00"
            },
            "NOKA.BA": {
                "symbol": "NOKA.BA",
                "name": "Nokia Corporation",
                "price": "557.50"
            }
        }
        """

        self.browser.get(self.finance_url)
        wait = WebDriverWait(self.browser, 10)

        btn_submit: WebElement = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[5]/div/div/div/div[2]/div[1]/div[3]/button[1]')))

        #remove mcap filter
        btn_remove_mcap = self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[5]/div/div/div/div[2]/div[1]/div[1]/div[2]/button')
        btn_remove_mcap.click()

        #remove default country
        btn_remove_eua = self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[5]/div/div/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/ul/li[1]/button')
        btn_remove_eua.click()

        #open dropdown with all regions
        btn_open_dropdown = self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[5]/div/div/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/ul/li/div/div')
        btn_open_dropdown.click()

        #force sleep until close regions dropdown
        time.sleep(1)
        try:
            #find region input checkbox
            input_region = self.browser.find_element(By.XPATH, f'//*[@id="dropdown-menu"]/div/div/ul/li/label/span[text()="{region}"]/parent::label')
            input_region.click()
        except:
            self.browser.quit()
            raise ValueError('Invalid region')

        btn_submit = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[5]/div/div/div/div[2]/div[1]/div[3]/button[1]')))
        btn_submit.click()

        records: Dict = {}

        end_of_file = False
        while end_of_file == False:
            try:
                
                table: WebElement = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="scr-res-table"]/div[1]')))
                btn_next: WebElement = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/section/div/div[2]/div[2]/button[3]')))

                table = wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="scr-res-table"]/div[1]')))
                
                df: pd.DataFrame = pd.read_html(table.get_attribute('innerHTML'))[0]
                df = df.rename(columns={"Symbol": "symbol", "Name": "name", "Price (Intraday)": "price"})[['symbol','name','price']]
                df["name"].fillna("", inplace = True)

                data: Dict = self.process_data(df)
                records.update(data)
                #results = pd.concat([results, df])

                btn_next = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/section/div/div[2]/div[2]/button[3]')))
                #btn_next.click()
                self.browser.execute_script("arguments[0].click();", btn_next)
            except ElementClickInterceptedException as e:
                print(e)
                raise RuntimeError('Did not possible load data')
                
            except TimeoutException as e:
                end_of_file = True

        self.browser.quit()

        return records

