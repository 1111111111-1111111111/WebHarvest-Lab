import json
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import hashlib
import os
from config.headers import HEADERS
import logging
import pandas as pd
import re
from urllib.parse import urljoin
semaphore = asyncio.Semaphore(10)  # 限制并发数


def setup_logging(log_path, mode):
    """设置日志配置"""
    global logger

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_path,
        filemode=mode,
        encoding='utf-8',
    )
    logger = logging.getLogger(__name__)

def normalize_url(url):
    if 'https://www.lghuitu.com/' not in url:
        url = urljoin("https://www.lghuitu.com/",url)
    return url

async def strore_async(session, url):
    """请求图片内容，保存"""
    async with semaphore:
        try:
            url = normalize_url(url)
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    print(f'{url} -> {response.status}')
                    return False
                content = await response.read()
                filename = hashlib.md5(content).hexdigest()

                # 从响应头获取内容类型
                content_type = response.headers.get('Content-Type', '')
                if 'image/jpeg' in content_type:
                    extension = '.jpg'
                elif 'image/png' in content_type:
                    extension = '.png'
                elif 'image/svg+xml' in content_type:
                    extension = '.svg'
                else:
                    extension = '.jpg'  # 默认扩展名

                filepath = os.path.join(r"D:\DATA\DATA\Pictures\流程图", f'{filename}{extension}')
                with open(filepath, 'wb') as f:
                    f.write(content)
                print(f'{url} 保存成功')

        except Exception as e:
            print(f'处理URL时出错 {url}: {e}')
            logger.info(url)
            return False


async def get_image_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [strore_async(session, url) for url in urls]
        await asyncio.gather(*tasks, return_exceptions=True)


async def get_image_urls_async(session, url):
    urls = []
    async with semaphore:
        try:
            async with session.get(url, headers=HEADERS, timeout=10) as resp:
                if resp.status != 200:
                    print(f'{url}响应出错！')
                    return False
                text = json.loads(await resp.text())
                url_tag = text['data']['list']
                for con in url_tag:


            return list(set(urls))
        except Exception as e:
            print(f'{url} 响应出错！{e}')
        return urls


async def get_ori_aysnc(all_urls):
    urls = []
    cnt = 0  # 将计数器移到外层，累积失败次数
    async with aiohttp.ClientSession() as session:
        tasks = [get_image_urls_async(session, url) for url in all_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                urls.extend(result)
    return list(set(urls))


async def main():
    log_path = r'D://pictures_log.log'
    mode = 'w'
    setup_logging(log_path, mode)
    url_list = []
    for i in range(1,730):
        url = rf"https://blog.csdn.net/community/home-api/v1/get-business-list?page={i}&size=20&businessType=blog&orderby=&noMore=false&year=&month=&username=weixin_61498557"
        url_list.append(url)

    print(f'{len(url_list)}共找到链接')
    all_urls = await get_ori_aysnc(url_list)
    # if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
    #     df = pd.read_csv(log_path, header=None, on_bad_lines='skip')
    #     for i in df.iloc[:, 1].tolist():
    #         pattern = r"(https://.*)"
    #         match = re.search(pattern, i)
    #         all_urls.append(match.group(1))

    print(f'总共发现{len(all_urls)}条链接')
    await get_image_async(all_urls)


if __name__ == '__main__':
    asyncio.run(main())
