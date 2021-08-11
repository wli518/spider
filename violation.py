from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import sys
from time import sleep
import time
from bs4 import BeautifulSoup
from concurrent import futures
from threading import Lock
import requests
import re

def mythread(option_n):
        #create Chrome web driver
        chromedriver = "C:\\Users\\xxx\\Desktop\\chromedriver"
        mydriver = webdriver.Chrome(chromedriver, options=webdriver.ChromeOptions())
        #start website through starting url
        mydriver.get(starting_url)

        # mydriver.maximize_window()
        # mydriver.implicitly_wait(1)
        sleep(1)
        #check 'By Neighborhood'
        mydriver.find_element_by_css_selector("input#ctl00_ContentPlaceHolder1_ck2").click()
        #click arrow in drop down list
        select = Select(mydriver.find_element_by_id("ctl00_ContentPlaceHolder1_lstLoc"))
        #take one Select option
        select.select_by_index(option_n)
        #click Search button
        mydriver.find_element_by_css_selector("input#ctl00_ContentPlaceHolder1_btSearch").click()
        sleep(1)

        #get page source of http://cels.baltimorehousing.org/TL_On_Map.aspx
        html = mydriver.page_source
        #create bs object to parse HTML page
        soup = BeautifulSoup(html, 'html.parser')
        #The list data keeps all violation records in 2021
        data=[]
        trs=soup.select("div.top.interior>table>tbody>tr>td>span>table.datagrid>tbody>tr")
        for tr in trs:
            if '/2021' in tr.get_text():
                cols = tr.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])
        #save all violation records to a file
        for e in data:
            #lock standard output and file output
            fw_lock.acquire()
            print(e[0]+"|"+e[2]+"|"+e[-1])
            fw_g.write(e[0] + "|" + e[2] + "|" + e[-1] + "\n")
            # unlock standard output and file output
            fw_lock.release()
        #close web driver
        mydriver.quit()
        return "option "+str(option_n)+" related page crawling is done"

        # trs = mydriver.find_elements_by_css_selector("div.top.interior>table>tbody>tr>td>span>table.datagrid>tbody>tr")
        # for tr in trs:
        #     address = tr.find_element_by_css_selector("td:nth-child(1)")
        #     date = tr.find_element_by_css_selector("td:nth-child(3)")
        #     line = address.text + "|" + date.text
        #     if date.text.endswith("2021"):
        #         print(line)

###################main######################
if __name__ == "__main__":
    #violation file location
    violation_file_dir="C:\\Users\\xxx\\Desktop\\violation\\"
    #create violation file location and open violation file for writing
    try:
        if not os.path.isdir(violation_file_dir):
            os.mkdir(violation_file_dir)
        fw_g=open(violation_file_dir+"violation2021.txt", "w")
    except:
        print("Cannot create directory "+violation_file_dir)
        print("Please run this script again")
        sys.exit(1)

    # create a lock for child threads to write violation files
    fw_lock=Lock()

    # access starting url
    starting_url = "http://cels.baltimorehousing.org/Search_On_Map.aspx"
    res = requests.get(starting_url)
    # get the total number of Select options
    select_list=re.findall('<select name="ctl00\$ContentPlaceHolder1\$lstLoc" id="ctl00_ContentPlaceHolder1_lstLoc">(.+?)</select>',res.text,re.DOTALL)
    option_list=re.findall('<option value=.+?</option>',select_list[0],re.DOTALL)
    l=len(option_list)-1
    print("total number of Select options(neighborhoods is " + str(l))

    # for testing purpose, set l to small number. This statement can be commented to crawl all option related pages.
    l = 101


    # start timer to calculate how long it takes to run
    start_time=time.time()

    # create 10 child threads and start them
    ex=futures.ThreadPoolExecutor(max_workers=10)
    print('main thread: starting')
    wait_for = [
        ex.submit(mythread, option_n) for option_n in range(1,l)
    ]
    # main thread waits all child threads to finish
    for f in futures.as_completed(wait_for):
        print('child thread: result: {}'.format(f.result()))
    #close violation file
    fw_g.close()
    # end timer
    end_time=time.time()
    print('time: %.2f' % (end_time-start_time))
    print("Please look file violation2021.txt under directory " + violation_file_dir)
