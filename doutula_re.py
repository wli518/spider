import os
import sys
import time
import re
import requests
import shutil
from concurrent import futures
from threading import Lock
import random

#This header is used to simulate browser
headers={
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }
#This function is threaded function
def mythread(page_n):

        os.mkdir(image_dir+str(page_n))
        url="http://www.doutula.com/article/list/?page="+str(page_n)
        res=requests.get(url,headers=headers)
        imglinks=re.findall("data-original=\"(.+?)\"",res.text)
        i=0
        for link in imglinks:
            i = i + 1
            #lock standard output
            display_lock.acquire()
            print(str(page_n)+"-"+str(i)+" - "+link)
            #unlock standard output
            display_lock.release()

            filename=link.split('/')[-1]
            #simulate human being behaviour
            time.sleep(round(random.random(),1))
            img=requests.get(link,headers=headers)
            with open(image_dir+str(page_n)+"\\"+filename,'wb') as fw:
                fw.write(img.content)

        return "page "+str(page_n)+" crawling is done"

###################main######################
if __name__ == "__main__":

    #image directory
    image_dir="C:\\Users\\myid\\Desktop\\images\\"
    #create image directory
    try:
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        os.mkdir(image_dir)
    except:
        print("Cannot create directory "+image_dir)
        print("Please run this script again")
        sys.exit(1)

    #create a lock for child threads to display message in standard output
    display_lock=Lock()

    #access starting url
    url = "http://www.doutula.com/article/list/?page=1"
    res = requests.get(url, headers=headers)

    #get the total number of pages
    pagelinks = re.findall("class=\"page-link\" href=.+?>(.+?)</a>", res.text)
    pagenums = []
    for p in pagelinks:
        if re.match(r"\d+",p):
            pagenums.append(int(p))
    l = pagenums[-1] #total number of pages
    print("total number of pages is "+str(l))

    # for testing purpose, set l to small number. This statement can be commented to crawl all pages.
    l = 11

    #start timer to calculate how long it takes to run
    start_time = time.time()

    #create 10 child threads and start them
    ex = futures.ThreadPoolExecutor(max_workers=10)
    print('main thread: starting')
    wait_for = [
        ex.submit(mythread, page_n) for page_n in range(1, l)
    ]
    #main thread waits all child threads to finish
    for f in futures.as_completed(wait_for):
        print('child thread: result: {}'.format(f.result()))

    #end timer
    end_time = time.time()
    print("total time: %.2f" % (end_time - start_time))
    print("Please look all sub directories with images under directory "+image_dir)
