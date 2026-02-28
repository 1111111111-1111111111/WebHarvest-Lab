import asyncio
import aiohttp
from bs4 import BeautifulSoup
from config.headers import HEADERS
from crawler_pictures.知乎_流程图 import download_images


async def crawler_pic1(session, url):
    """爬取第一级页面，获取图片详情页链接"""
    base_url = 'https://www.liuchengtu.com'
    urls = []

    try:
        async with session.get(url, headers=HEADERS, timeout=30) as response:
            if response.status != 200:
                print(f'爬取失败！状态码: {response.status} -> {url}')
                return urls

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            pic_urls = soup.find_all('div', class_='template-info')

            if not pic_urls:
                print(f'没有找到图片元素！ -> {url}')
                return urls

            for pic in pic_urls:
                a_tag = pic.find('a')
                if a_tag and a_tag.get('href'):
                    href = a_tag.get('href')
                    if not href.startswith(base_url):
                        href = f'{base_url}{href}'
                    urls.append(href)

    except Exception as e:
        print(f'爬取异常: {e} -> {url}')

    return urls


async def crawler_pic2(session, url):
    """爬取第二级页面，获取实际图片链接"""
    try:
        async with session.get(url, headers=HEADERS, timeout=30) as response:
            if response.status != 200:
                print(f'爬取失败！状态码: {response.status} -> {url}')
                return None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            pic_div = soup.find('div', class_='template-pic-show')

            if not pic_div:
                print(f'没有找到图片展示区域！ -> {url}')
                return None
            else:
                temp_div = pic_div.find('template-info-content-main')
                if not temp_div:
                    print(f'未找到图片链接 -> {url}')
                    return None
                else:
                    return temp_div.get('src')

    except Exception as e:
        print(f'爬取异常: {e} -> {url}')
        return None


async def crawler_sig_pic(urls):
    """并发爬取第一级页面"""
    async with aiohttp.ClientSession() as session:
        tasks = [crawler_pic1(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_urls = []
        for result in results:
            if isinstance(result, Exception):
                print(f'任务执行异常: {result}')
            elif isinstance(result, list):
                all_urls.extend(result)

        return all_urls


async def crawler_sec_pic(urls):
    """并发爬取第二级页面"""
    async with aiohttp.ClientSession() as session:
        tasks = [crawler_pic2(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        pic_urls = []
        for result in results:

            if isinstance(result, Exception):
                print(f'任务执行异常: {result}')
            elif isinstance(result,str):
                pic_urls.append(result)

        return pic_urls


def generate_urls():
    """生成要爬取的页面URL"""
    urls = []
    base_url = 'https://www.liuchengtu.com/template/'

    for i in range(1, 50):
        if i == 1:
            url = f'{base_url}lct-g0h0o1k0.html'
        else:
            url = f'{base_url}lct-h0g0o1k0p{i}.html'
        urls.append(url)

    return urls


async def main():
    """主函数"""
    # 生成所有要爬取的页面URL
    all_urls = generate_urls()
    print(f'开始爬取 {len(all_urls)} 个页面...')

    # 第一步：获取所有图片详情页链接
    sig_urls = await crawler_sig_pic(all_urls)
    print(f'成功爬取 {len(sig_urls)} 个详情页链接！')

    if not sig_urls:
        print('没有找到详情页链接，程序结束！')
        return

    # 第二步：获取所有实际图片链接
    sec_urls = await crawler_sec_pic(sig_urls)
    sec_urls = [url for url in sec_urls if url]  # 过滤掉None值
    print(f'成功爬取 {len(sec_urls)} 张图片链接！')

    if not sec_urls:
        print('没有找到图片链接，程序结束！')
        return

    # 第三步：下载图片
    results = await download_images(sec_urls, r'D:\DATA\pictures\流程图')
    success_count = sum(results)
    print(f'成功下载 {success_count} 张图片！')


if __name__ == '__main__':
    asyncio.run(main())