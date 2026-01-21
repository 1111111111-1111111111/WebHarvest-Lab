import requests
from bs4 import BeautifulSoup
import pandas as pd
import time,random
import hashlib
import os
from urllib.parse import urlparse,urljoin
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}
#
def normalize_url(url):
    """
    将URL转换为标准形式
    """
    if url.startswith('//'):
        url = 'https:' + url

    return url


def get_src(urls):
    path = r"D:\DATA\DATA\Pictures\流程图"
    src_list = []
    for url in urls:
        response = requests.get(url, headers=HEADERS,timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        img_tag = soup.find_all('img')

        for img in img_tag:
            src = normalize_url(img['src'])
            response = requests.get(src,headers=HEADERS,timeout=10)
            extension = response.headers.get('Content-Type', '').split('/')[1]

            filename = hashlib.md5(response.content).hexdigest()
            filepath = os.path.join(path, f"{filename}.{extension}")
            src_list.append(src)

            with open(filepath,'wb') as f:
                f.write(response.content)
            print(f"{src} -> {filename}")
        time.sleep(random.uniform(1,3))
    df = pd.DataFrame(src_list)
    df.to_csv('src.csv',header=False,mode='a',index=False)

def get_page():
    path = r"p.txt"
    all_urls = []

    for i in range(15, 30):
        url = rf"https://www.edrawsoft.cn/software/flowchart/page/{i}/"
        try:
            response = requests.get(url,headers=HEADERS,timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            if '该页面不存在，请访问官网主页 www.edrawsoft.cn' in soup:
                break

            a_tag = soup.find_all('h2', {'class': 'entry-title'})
            for a in a_tag:
                href_tag = a.find('a')
                all_urls.append(href_tag['href'])

            get_src(all_urls)
            all_urls = []

            df = pd.DataFrame(all_urls)
            df.to_csv(path, mode='a', index=False, header=False)
            time.sleep(random.uniform(1,3))
        except Exception:
            print(f'{url} 请求失败')
            print(f"[{datetime.now()}] 请求URL失败: {url}")

if __name__ == '__main__':
    get_page()
