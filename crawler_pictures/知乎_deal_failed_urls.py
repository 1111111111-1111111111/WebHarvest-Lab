import pandas as pd
import requests
import os
import aiohttp
import asyncio

from crawler_pictures.知乎_流程图 import download_images


def read_urls(path):
    """读取失败的URL"""
    if os.path.exists(path):
        urls = pd.read_csv(path, header=None,on_bad_lines='skip', encoding='utf-8-sig').iloc[:,0]
        print(f"已读取失败的URL: {path}")
        return urls
    else:
        print(f"文件不存在: {path}")
        return []
async def main():
    pic_path = r"D:\DATA\pictures\流程图"
    txt_path = r"D:\DATA\pictures\failed_urls.txt"

    urls = read_urls(txt_path)
    print(f'已读取失败的URL: {len(urls)}')
    results = await download_images(urls,pic_path)

    # 统计结果
    success_count = sum(1 for r in results if r is True)
    print(f"下载完成: {success_count}/{len(urls)} 成功")

if __name__ == '__main__':
    asyncio.run(main())