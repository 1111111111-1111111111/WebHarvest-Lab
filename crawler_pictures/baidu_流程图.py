import requests
from config.headers import HEADERS
from bs4 import BeautifulSoup
def crawler_pic(url):
    resp = requests.get(url,headers=HEADERS,timeout=30)
    soup = BeautifulSoup(resp.text,'lxml')
    print(soup)

def main():
    url = r"https://image.baidu.com/search/acjson?tn=resultjson_com&word=%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91%E6%B5%81%E7%A8%8B%E5%9B%BE&ie=utf-8&fp=result&fr=&ala=0&applid=6871356711576668495&pn=150&rn=30&nojc=0&gsm=96&newReq=1"
    crawler_pic(url)

if __name__ == '__main__':
    main()