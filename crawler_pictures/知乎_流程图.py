import time

import pandas as pd
import requests
import re
import json
import hashlib
import aiohttp
import asyncio
from config.headers import headers
import os
import random
from urllib.parse import unquote

failed_urls = set()


def write_failed(path):
    global failed_urls
    if failed_urls:
        failed_file = os.path.join(os.path.dirname(path), 'failed_urls_freedgo.txt')
        df = pd.DataFrame(failed_urls)
        df.to_csv(failed_file, mode='a', index=False, header=False, encoding='utf-8-sig')
        print(f"已保存失败的URL到: {failed_file}")


def read_failed(path):
    failed_file = os.path.join(os.path.dirname(path), 'failed_urls.txt')
    if os.path.exists(failed_file):
        urls = pd.read_csv(failed_file, header=None, on_bad_lines='skip', encoding='utf-8-sig')
        print(f"已读取失败的URL: {failed_file}")
        if urls.empty:
            return urls.iloc[:, 0]
        else:
            return []


async def store_image(session, url, save_dir, semaphore=8, proxy=None):
    """下载并保存单张图片"""
    global failed_urls
    if proxy:
        retry_count = 0
        max_retries = len(proxy)
        while retry_count < max_retries:
            async with semaphore:
                try:
                    async with session.get(url, timeout=10, headers=headers, proxy=proxy[retry_count]) as resp:
                        if retry_count == max_retries:
                            return False
                        if resp.status != 200:
                            failed_urls.add(url)
                            print(f"请求失败: {url}, 状态码: {resp.status}")
                            retry_count += 1
                            continue

                        data = await resp.read()
                        md5 = hashlib.md5(data).hexdigest()

                        # 获取文件扩展名
                        content_type = resp.headers.get('content-type', '')
                        if 'image/' in content_type:
                            extension = content_type.split('/')[-1]
                        else:
                            # 从URL中提取扩展名
                            extension = url.split('.')[-1].split('?')[0]
                            if len(extension) > 4 or extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                extension = 'jpg'

                        filename = f'{md5}.{extension}'
                        filepath = os.path.join(save_dir, filename)

                        # 避免重复下载
                        if not os.path.exists(filepath):
                            with open(filepath, 'wb') as f:
                                f.write(data)
                            print(f"已保存: {filename}")
                        else:
                            print(f"文件已存在: {filename} -> {url}")
                        return True

                except Exception as e:
                    failed_urls.add(url)
                    print(f"下载失败 {url}: {str(e)}")
                    return False
    else:
        async with semaphore:
            try:
                async with session.get(url, timeout=30, headers=headers) as resp:
                    # time.sleep(random.uniform(1,3))
                    if resp.status != 200:
                        failed_urls.add(url)
                        print(f"请求失败: {url}, 状态码: {resp.status}")
                        return False

                    data = await resp.read()
                    md5 = hashlib.md5(data).hexdigest()

                    # 获取文件扩展名
                    content_type = resp.headers.get('content-type', '')
                    if 'image/' in content_type:
                        extension = content_type.split('/')[-1]
                    else:
                        # 从URL中提取扩展名
                        extension = url.split('.')[-1].split('?')[0]
                        if len(extension) > 4 or extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            extension = 'jpg'

                    filename = f'{md5}.{extension}'
                    filepath = os.path.join(save_dir, filename)

                    # 避免重复下载
                    if not os.path.exists(filepath):
                        with open(filepath, 'wb') as f:
                            f.write(data)
                        print(f"已保存: {filename}")
                    else:
                        print(f"文件已存在: {filename} -> {url}")
                    return True

            except Exception as e:
                failed_urls.add(url)
                print(f"下载失败 {url}: {str(e)}")
                return False


async def download_images(urls, save_dir, max_concurrent=3, proxy=False):
    """并发下载多张图片"""
    if proxy:
        df = pd.read_csv(r"D:\proxy\proxy_pool.csv", header=None)
        proxy = df.values.tolist()

    semaphore = asyncio.Semaphore(max_concurrent)  # 设置最大并发数
    # 创建带有代理的会话
    connector = aiohttp.TCPConnector(ssl=False)  # 禁用SSL验证以提高速度
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        tasks = [store_image(session, url, save_dir, semaphore, proxy) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        write_failed(save_dir)
        return results


def extract_urls(path):
    """从JSON文件中提取图片URL"""
    all_urls = []
    file_path = os.path.join(path, '1.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            con = f.read()

            # 改进的正则表达式，匹配常见图片格式
            pattern = r'"thumburl":"([^"]+)"'
            urls = re.findall(pattern, con, re.IGNORECASE)

            urls = [url.replace('\\u0026', "&") for url in urls]
            # for url in urls:
            #     new_url = unquote(url)
            #     while True:
            #         if new_url != url:
            #             url = unquote(new_url)
            #             new_url = url
            #         else:
            #             break
            all_urls.extend(urls)
        # 去重
        unique_urls = list(set(all_urls))

        # 保存URL到文件（可选）
        if unique_urls:
            url_file = os.path.join(os.path.dirname(file_path), 'urls.txt')
            if os.path.exists(url_file):
                # 读取已存在的URL
                exi_urls = pd.read_csv(url_file, header=None, on_bad_lines='skip', encoding='utf-8-sig')
                if not exi_urls.empty:
                    exi_urls = exi_urls.iloc[:, 0].to_list()
                exi_urls = list(exi_urls)
            else:
                exi_urls = []
            exi_urls.extend(unique_urls)
            df = pd.DataFrame(exi_urls, columns=['url'])
            df.to_csv(url_file, header=False, mode='a', index=False, encoding='utf-8-sig')
            print(f"找到 {len(unique_urls)} 个图片URL，已保存到: {url_file}")
        print(f"找到 {len(unique_urls)} 个图片URL")

        return unique_urls

    except Exception as e:
        print(f"提取URL失败: {str(e)}")
        return []


async def main():
    # 配置路径
    json_file = r"D:\DATA\pictures"  # 实际JSON文件路径
    save_dir = r"D:\DATA\pictures\教育领域流程图"

    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)

    # 提取URL
    urls = extract_urls(json_file)

    urls.extend(read_failed(save_dir))

    if not urls:
        print("未找到图片URL")
        return
    # urls = pd.read_csv(r"D:\DATA\pictures\urls.txt", header=None,on_bad_lines='skip', encoding='utf-8-sig').iloc[:,0]
    # urls = [url.strip("\\") for url in urls]
    # 下载图片
    print(f"开始下载 {len(urls)} 张图片...")
    results = await download_images(urls, save_dir)

    # 统计结果
    success_count = sum(1 for r in results if r is True)
    print(f"下载完成: {success_count}/{len(urls)} 成功")


if __name__ == '__main__':
    asyncio.run(main())
