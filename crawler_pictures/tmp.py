import requests
from bs4 import BeautifulSoup

from crawler_pictures.crawler_picture import HEADERS


def main():
    url = r"https://image.baidu.com/search/acjson?tn=resultjson_com&word=%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91%E6%B5%81%E7%A8%8B%E5%9B%BE&ie=utf-8&fp=result&fr=&ala=0&applid=9019058475376537827&pn=990&rn=30&nojc=0&gsm=294&newReq=1"
    resp = requests.get(url,headers=HEADERS,timeout=30).json()
    print(resp)

if __name__ == '__main__':
    main()