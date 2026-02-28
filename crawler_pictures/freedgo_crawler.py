import pandas as pd
import requests
import aiohttp
import asyncio
from config.headers import headers
from bs4 import BeautifulSoup
from crawler_pictures.知乎_流程图 import download_images
import time
import random
async def crawler_main(session,url,semaphore=3):
    all_urls = []
    try:
        async with semaphore:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f'爬取失败！状态码: {response.status} -> {url}')

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                pic_urls = soup.find('div', {'id':'masonry'})
                # print(pic_urls)
                if not pic_urls:
                    print(f'未找到图片 -> {url}')
                    return all_urls

                img_tags = pic_urls.find_all('img')
                if not img_tags:
                    print(f'未找到图片 -> {url}')
                    return all_urls

                for pic_url in img_tags:
                    pic_url = pic_url.get('src')
                    all_urls.append(pic_url)

                return all_urls
    except Exception as e:
        print(f'爬取异常: {e} -> {url}')
async def crawler(urls,max_concurrent=3):
    all_urls = []
    semaphore = asyncio.Semaphore(max_concurrent)  # 设置最大并发数
    async with aiohttp.ClientSession() as session:
        tasks = [crawler_main(session, url,semaphore) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f'任务执行异常: {result}')
            elif isinstance(result, list):
                all_urls.extend(result)
    return all_urls

async def main():
    start = 30
    end = 100  # 1091
    step = 1
    all_urls = []
    for i in range(start,end,step):
        "%5B1854%5D %5B1907%5D %5B1855%5D %5B1853%5D"
        url = f'https://www.freedgo.com/new/search/3/0/d_0_3_0_0_{i}_0_0.html'
        all_urls.append(url)
    result = await crawler(all_urls)
    df = pd.DataFrame(result)
    df.to_csv(r'freedgo.txt',index=False,header=False,encoding='utf-8-sig')

    print(f'总共抓取到 {len(result)} 张图片')

    await download_images(result, r'D:\DATA\pictures\流程图')


if __name__ == '__main__':
    asyncio.run(main())