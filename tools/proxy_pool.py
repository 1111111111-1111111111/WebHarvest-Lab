import aiohttp
import asyncio

import pandas as pd
from bs4 import BeautifulSoup
from config.headers import HEADERS
async def crawler(urls):
    all_urls = []
    semaphore = asyncio.Semaphore(10)
    async def crawler_with_semaphore(url):
        proxies = []  # 用于存储当前URL获取到的所有代理
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get(url,headers=HEADERS,timeout=30) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    trs = soup.find('tbody')
                    for tr in trs.find_all('tr'):
                        ip = tr.find_all('td')[0].text.strip()
                        port = tr.find_all('td')[1].text.strip()

                        # 添加多种协议格式的代理
                        proxies.append([
                            'http', f'http://{ip}:{port}','https', f'https://{ip}:{port}'
                        ])
                    return proxies

    results = await asyncio.gather(*[crawler_with_semaphore(url) for url in urls], return_exceptions=True)

    for result in results:

        if isinstance(result, Exception):
            print(f'任务执行异常: {result}')
        elif isinstance(result, list):
            all_urls.extend(result)
    return all_urls


async def val_proxy(proxies):
    """验证代理"""
    true_proxys = []
    tmp = []
    semaphore = asyncio.Semaphore(10)

    async def validate_single_proxy(proxy):
        """验证单个代理"""
        async with semaphore:
            try:
                # 使用代理请求百度测试
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            url="http://www.baidu.com",
                            proxy=proxy[1] or proxy[3],  # aiohttp使用proxy参数
                            timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            true_proxys.append([proxy[1],proxy[3]])
                            return proxy
                        else:
                            return None
            except Exception as e:
                print(f'代理不可用:{proxy}, 错误: {e}')
                return None

    # 创建所有验证任务
    tasks = [validate_single_proxy(proxy) for proxy in proxies]

    # 并发执行所有任务
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理结果
    for result in results:
        if isinstance(result, Exception):
            print(f'任务执行异常: {result}')
        elif result:  # 如果result不是None
            tmp.append(result)

    return true_proxys  # 返回可用代理列表
async def main():
    urls = []
    for i in range(1,101):
        if i == 1:
            url = r"https://www.89ip.cn"
        else:
            url = rf"https://www.89ip.cn/index_{i}.html"
        urls.append(url)
    all_urls= await crawler(urls)

    print(f'共抓取到 {len(all_urls)} 个代理')
    result = await val_proxy(all_urls)
    df = pd.DataFrame(result)
    df.to_csv(r"D:\proxy\proxy_pool.csv", index=False, header=False,encoding='utf-8-sig')

if __name__ == '__main__':
    asyncio.run(main())