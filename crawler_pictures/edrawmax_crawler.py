import requests
import aiohttp
import asyncio
from config.headers import headers
from bs4 import BeautifulSoup
from crawler_pictures.知乎_流程图 import download_images
import pandas as pd

def normalize_url(url):
    if not url.startswith('http'):
        url = f'https://www.edrawmax.cn{url}'
    return url

async def deal_sec(session, url):
    try:
        async with session.get(url, headers=headers, timeout=30) as response:
            if response.status != 200:
                print(f'爬取失败！状态码: {response.status} -> {url}')

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')



            div_tag = soup.find_all('img', {'class': 'mo-work--img'})
            if not div_tag:
                # div_tag = soup.find_all('img',{'class':'no-work'})
                print(f'没有找到图片元素！ -> {url}')
            for div in div_tag:
                if div:
                    return [div['src']]

    except Exception as e:
        print(f'爬取异常: {e} -> {url}')


async def crawler_second(urls):
    all_urls = []
    async with aiohttp.ClientSession() as session:
        tasks = [deal_sec(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f'任务执行异常: {result}')
            elif isinstance(result, list):
                all_urls.extend(result)
        return all_urls

async def deal_sig(session,url):
    all_urls = []
    try:
        async with session.get(url, headers=headers, timeout=30) as response:
            if response.status != 200:
                print(f'爬取失败！状态码: {response.status} -> {url}')

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # print("*"*30)
            # print(soup)
            # print("*"*30)
            # print(url)
            # print("*"*30)

            div_tag = soup.find_all('img', {'class': 'mo-work--img'})
            if not div_tag:
                print(f'没有找到图片元素！ -> {url}')

            for div in div_tag:
                a_tag = div['src']
                all_urls.append(a_tag)
            return all_urls

    except Exception as e:
        print(f'爬取异常: {e} -> {url}')
async def crawler_sig(urls):
    all_urls = []
    async with aiohttp.ClientSession() as session:
        tasks = [deal_sig(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f'任务执行异常: {result}')
            elif isinstance(result, list):
                all_urls.extend(result)
        return all_urls
async def main():
    all_urls = []
    # 社区精选1000 组织结构1002 计算机1003-118
    num = 1003
    end = 118
    for i in range(1,end):
        url = rf"https://www.edrawmax.cn/templates/{num}/{i}/0"
        all_urls.append(url)

    sig_urls = await crawler_sig(all_urls)
    print(f'找到{len(sig_urls)}')
    df = pd.DataFrame(sig_urls)
    df.to_csv(r'edrawmax.csv',index=False,header=False,encoding='utf-8-sig')
    # second_urls = await crawler_second(sig_urls)
    # print(f'找到{len(second_urls)}')
    await download_images(sig_urls, r'D:\DATA\pictures\流程图1')

if __name__ == '__main__':
    asyncio.run(main())