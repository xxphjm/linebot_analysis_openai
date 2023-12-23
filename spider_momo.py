import re
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

delay_choices = [8, 5, 10, 6, 4, 9, 12, 7]  #延遲的秒數
delay = random.choice(delay_choices)  #隨機選取秒數
keyword = '理膚寶水'
pages = 12
user_agent = UserAgent()
headers={ 'user-agent': user_agent.random }
urls = []
for page in range(1, pages+1):
    url = 'https://m.momoshop.com.tw/search.momo?_advFirst=N&_advCp=N&curPage={}&searchType=1&cateLevel=2&ent=k&searchKeyword={}&_advThreeHours=N&_isFuzzy=0&_imgSH=fourCardType'.format(page, keyword)
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, features="lxml")
        for item in soup.select('li.goodsItemLi > a'):
            urls.append('https://m.momoshop.com.tw'+item['href'])
            time.sleep(delay)
urls = list(set(urls))
print('總筆數：',len(urls))

df = []
# driver = webdriver.Chrome('./chromedriver-win64/chromedriver.exe')
chrome_service = Service('./chromedriver-win64/chromedriver.exe')
chrome_options = Options()
chrome_options.add_argument(f"--user-agent={user_agent.random}")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

try:
    for i, url in enumerate(urls):
        columns = []
        values = []

        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text)
        # 標題
        title = soup.find('meta',{'property':'og:title'})['content']
        # 品牌
        brand = soup.find('meta',{'property':'product:brand'})['content']
        # 連結
        link = soup.find('meta',{'property':'og:url'})['content']
        # 原價
        try:
            price = re.sub(r'\r\n| ','',soup.find('del').text)
        except:
            price = ''
        # 特價
        amount = soup.find('meta',{'property':'product:price:amount'})['content']
        # 類型
        cate = ''.join([i.text for i in soup.findAll('article',{'class':'pathArea'})])
        cate = re.sub('\n|\xa0',' ',cate)

        # 總銷售量
        driver.get(url)
        # total_sales_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'productTotalSales')))
        total_sales_element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, 'productTotalSales')))
        # total_sales = total_sales_element.text
        total_sales = driver.find_element_by_class_name('productTotalSales').text

        # 平均星星數
        star = driver.find_element_by_class_name('productRatingScore').text
        # print('total_sales:', total_sales, 'star:', star)

        # 商品號------
        product_id = soup.find('meta',{'property':'product:retailer_item_id'})['content']

        #商品評論
        product_reviews=[]
        url_product = 'https://m.momoshop.com.tw/goodsComment.momo?i_code={}&goodsCanReviews=1&isSwitchGoodsReviews=1&isSwitchGoodsTotalSales=1&isSwitchGoodsComment=1'.format(product_id)
        driver.get(url_product)
        original_height = driver.execute_script("return document.body.scrollHeight")
        #滾動頁面到最底加載完所有留言
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == original_height:
                time.sleep(0.5)
                break
            original_height=new_height

        # comment_all = driver.find_elements_by_xpath("//div[contains(@class,'CommentContainer') and not(following-sibling::div[contains(@class,'ReplyContainer')])]") # 過濾廠商回覆評論

        # for index,comment in enumerate(comment_all):
        #     # print(comment.text)
        #     product_reviews.append(comment.text)
        # -------------------
        comment_all = driver.find_elements_by_css_selector(".reviewCard")
        for index,comment in enumerate(comment_all):
            #[0] 過濾掉廠商回覆
            comment_date = comment.find_elements_by_css_selector(".Info .Date")[0].text
            comment_text = comment.find_elements_by_css_selector(".CommentContainer .Comment")[0].text
            # print(i,comment_date,comment_text)
            product_reviews.append({"留言時間":comment_date, "留言內容":comment_text})
        # -------------------

        print(f'==================  {i}  ==================')    
        print(title)
        print(brand)
        # print("product_reviews",product_reviews,len(product_reviews))

        # columns += ['title', 'product_id', 'brand', 'link', 'price', 'amount', 'cate', 'total_sales', 'star']
        # values += [title, product_id, brand, link, price, amount, cate, total_sales, star]
        columns += ['title', 'product_id', 'brand', 'link', 'price', 'amount', 'cate', 'total_sales', 'star', 'reviews']
        values += [title, product_id, brand, link, price, amount, cate, total_sales, star, product_reviews]

        ndf = pd.DataFrame(data=values, index=columns).T
        df.append(ndf)
        # print(df)
finally:
    time.sleep(delay)
    driver.quit()
df=pd.concat(df, ignore_index=True)
df.to_csv('./MOMO.csv')
driver.close()