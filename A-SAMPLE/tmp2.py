from aiohttp import ClientTimeout,TCPConnector
import aiohttp
import asyncio
from config.headers import HEADERS
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
import random
import logging

BASE_DOMAIN = 'https://vaas.vn'
OUTPUT_FILE = r"D:\test"
CONCURRENCY = 8
CHUNCK_SIZE = 50
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0

def normalize_url(base,url):
    """规范化URL"""
    if url.startswith('/'):
        return urljoin(base, url)
    else:
        return url

def setup_logging():
    """设置日志"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger

async def fetch_text(session, url,*,retries=MAX_RETRIES):
    """获取内容"""
    backoff = INITIAL_BACKOFF
    for attempt in range(1,retries+1):
        try:
            async with session.get(url, headers=HEADERS, timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                if resp.status != 200:
                    return None
                text = await resp.text()
                return text
        except asyncio.CancelledError:
            raise
        except Exception as e:
            if attempt == retries:
                logger.info(f'[ERROR] {url} failed：{e}')
                return None
            await asyncio.sleep(backoff+random.random()*0.3)
            backoff *=2

async def get_content_from_url(session,url,semaphore):
    """从内容页提取标题与正文"""
    async with semaphore:
        text = await fetch_text(session,url)
        if not text:
            return None

        soup = BeautifulSoup(text, 'html.parser')
        con = ""

        content = soup.find('div', {'id': 'block-vaas-content'})
        if content:
            con += content.get_text(strip=True)

        return con if con else None


async def fetch_content_batch(session, urls, concurrency=CONCURRENCY):
    """使用semaphore控制并发，按照完成顺序yield内容"""
    semaphore = asyncio.Semaphore(concurrency)

    tasks = [asyncio.create_task(get_content_from_url(session,u,semaphore)) for u in urls]
    for task in asyncio.as_completed(tasks):
        try:
            res = await task
            yield res
        except Exception:
            yield None


async def get_content_urls_from_page(session, url):
    """从单个页面提取内容链接"""
    content_urls = []
    try:
        async with session.get(url, headers=HEADERS, timeout=60) as resp:
            if resp.status != 200:
                return []
            text = await resp.text()
            soup = BeautifulSoup(text, 'html.parser')

            li_tag = soup.find_all('li',{'class':'category-list-item'})
            for li in li_tag:
                if li:
                    h2 = li.find('h2')
                    if h2:
                        a = li.find('a')
                        if a:
                            href = a.get('href')
                            if href:
                                href = normalize_url(href)
                                content_urls.append(href)
            return content_urls
    except Exception as e:
        logger.info(f'Error fetching {url}:{e}')
        return []
async def get_content_urls_from_listing(session,url,base=BASE_DOMAIN):
    """从一个列表/分页页提取文章链接，注意根据实际页面结构调整选择器"""
    text = await fetch_text(session,url)
    if not text:
        return []
    soup = BeautifulSoup(text,'html.parser')
    content_urls = []
    li_tags = soup.find_all('li',{'class':'category-list-item'})
    for li in li_tags:
        a = li.find('a')
        if a and a.get('href'):
            href = normalize_url(base,a['href'])
            if href:
                content_urls.append(href)
    return list(set(content_urls))

def save_chunk(rows,output_file=OUTPUT_FILE):
    """以追加方式保存到CSV"""
    if not rows:
        return
    df = pd.DataFrame(rows)
    filepath = os.path.join(output_file,'seen.csv')
    df.to_csv(filepath,encoding='utf-8-sig',header=False,mode='a',index=False)

async def crawler_async(urls):
    """下载内容并分批写盼"""
    connector = TCPConnector(limit_per_host=CONCURRENCY,ssl=False)  # ssl False根据需要调整
    timeout= ClientTimeout(total=REQUEST_TIMEOUT)
    async with aiohttp.ClientSession(headers=HEADERS,connector=connector,timeout=timeout,trust_env=False) as session:
        saved = 0
        buffer = []
        async for text in fetch_content_batch(session,urls,concurrency=CONCURRENCY):
            if text:
                res = {'content':text,'label':'AGRICULTURE_CULTURE'}
                buffer.append(res)
                saved += 1
                if len(buffer) >= CHUNCK_SIZE:
                    save_chunk(buffer)
                    logger.info(f'[INFO] saved {saved} items')
                    buffer = []
                # 小随机等待，减缓爬取节奏，降低触发风控概率
                await asyncio.sleep(random.uniform(0.1,0.4))
        # 保存剩下的
        if buffer:
            save_chunk(buffer)
            logger.info(f'[DONE] total saved:{saved}')

async def crawler_content_async(urls,base=BASE_DOMAIN):
    """并行抓取多个列表页，汇总所有内容链接"""
    connector = TCPConnector(limit_per_host=4,ssl=False)
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)

    async with aiohttp.ClientSession(headers=HEADERS,connector=connector,timeout=timeout,trust_env=False) as session:
        tasks = [get_content_urls_from_listing(session, u,base) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        content_urls = []
        for result in results:
            if isinstance(result, list):
                content_urls.extend(result)
        return list(set(content_urls))


async def main():
    url_list = []
    for i in range(0,3):  # 226
        if i == 1:
            url = rf'https://vaas.vn/vi/nong-nghiep-nuoc-ngoai'
        else:
            url = rf'https://vaas.vn/vi/nong-nghiep-nuoc-ngoai?page={i}'
        url_list.append(url)

    content_urls = await crawler_content_async(url_list,base=BASE_DOMAIN)
    logger.info(f'[INFO] Found {len(content_urls)} content URLs')
    if not content_urls:
        logger.info('[WARN] No content URLs found.')
        return
    # 可能需随机打乱顺序，避免一直按同序访问
    random.shuffle(content_urls)
    await crawler_async(content_urls)

if __name__ == '__main__':
    logger = setup_logging()
    asyncio.run(main())
