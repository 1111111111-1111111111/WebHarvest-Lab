import requests
import aiohttp
import asyncio
from config.headers import HEADERS
from bs4 import BeautifulSoup
from crawler_pictures.知乎_流程图 import download_images
async def crawler_main(session,url):
    all_urls = []
    try:
        async with session.get(url, headers=HEADERS, timeout=30) as response:
            if response.status != 200:
                print(f'爬取失败！状态码: {response.status} -> {url}')

            html = await response.json()
            data = html.get('data')
            if not data:
                print(f'没有找到图片元素！ -> {url}')
                return all_urls

            file_list = data.get('file_list')
            if not file_list:
                print(f'没有找到图片元素！ -> {url}')
                return all_urls

            for item in file_list:
                url = item.get('avatar_url')
                all_urls.append(url)
            return all_urls

    except Exception as e:
        print(f'爬取异常: {e} -> {url}')
async def crawler(urls):
    all_urls = []
    async with aiohttp.ClientSession() as session:
        tasks = [crawler_main(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f'任务执行异常: {result}')
            elif isinstance(result, list):
                all_urls.extend(result)
        return all_urls
async def main():
    end = 10000
    step = 99
    all_urls = []
    for i in range(0,end,step):
        "%5B1854%5D %5B1907%5D %5B1855%5D %5B1853%5D"
        url = f'https://api.boardmix.cn/api/cmt/files/search?special_data=1&tag_id_arr%5B%5D=%5B1853%5D&cursor={i}&size=99&order=6'
        all_urls.append(url)
    sig_urls = await crawler(all_urls)
    print(f'找到{len(sig_urls)}')
    await download_images(sig_urls, r'D:\DATA\pictures\流程图')
if __name__ == '__main__':
    asyncio.run(main())