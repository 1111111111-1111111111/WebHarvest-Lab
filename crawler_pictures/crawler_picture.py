import os
import time
import random
import hashlib
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
import mimetypes
from bs4 import BeautifulSoup


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}


def pictures_crawler(urls):
    folder_picture = r"D:\DATA\Pictures\流程图"
    os.makedirs(folder_picture, exist_ok=True)

    srcs = get_src(urls)
    df = pd.DataFrame(srcs)
    df.to_csv('src.csv', mode='a', index=False, header=False)

    for url in srcs:
        url = str(url).strip()
        if not url:
            continue
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"[{datetime.now()}] 请求图片失败: {url}  错误: {e}")
            time.sleep(random.uniform(1, 3))
            continue

        # 计算 md5
        md5_name = hashlib.md5(resp.content).hexdigest()

        # 提取扩展名
        ctype = resp.headers.get('Content-Type', '').split(';')[0].strip().lower()
        ext = ""
        if ctype:
            guessed = mimetypes.guess_extension(ctype)
            if guessed:
                ext = guessed.lstrip('.')
            else:
                # 常见图像类型手动映射
                mapping = {
                    'image/jpeg': 'jpg',
                    'image/jpg': 'jpg',
                    'image/png': 'png',
                }
                ext = mapping.get(ctype)
        if not ext:
            ext = 'jpg'  # 兜底

        file_path = os.path.join(folder_picture, f"{md5_name}.{ext}")
        try:
            with open(file_path, "wb") as f:
                f.write(resp.content)
            print(f"{url}图片写入成功")
        except Exception as e:
            print(f"[{datetime.now()}] 写文件失败: {file_path} 错误: {e}")

        time.sleep(random.uniform(1, 3))

def get_src(urls):
    for url in urls:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            con = soup.find('div', {'id': 'article_content'})

            urls_tag = con.find_all('img')
            all_src = []
            for img in urls_tag:
                all_src.append(img.get('src'))

            return all_src
        except Exception as e:
            print(f"请求URL失败: {e}")
            return []


def auto_read_growing_file(file_path, last_position=0, interval=8):
    """
    每 interval 秒自动读取正在增长的文件内容
    last_position 表示已读的行数（row count），首次运行为0。
    返回值为更新后的 last_position。
    """
    no_new_content_count = 0
    max_no_content_count = 3  # 最大无新内容次数

    while True:
        try:
            if not os.path.exists(file_path):
                print(f"[{datetime.now()}] 文件不存在：{file_path}，等待...")
                no_new_content_count += 1
            else:
                # 从指定行数开始读取
                new_content = pd.read_csv(file_path, header=None, skiprows=last_position, on_bad_lines='skip')
                rows = len(new_content)
                if rows > 0:
                    try:
                        urls = new_content.iloc[:, 0].astype(str).str.strip().tolist()
                    except Exception:
                        urls = [str(x).strip() for x in new_content.iloc[:, 0].tolist()]

                    print(f"[{datetime.now()}] 读取到新内容：{rows} 行")

                    pictures_crawler(urls)  # 处理新内容
                    last_position += rows
                    no_new_content_count = 0
                else:
                    no_new_content_count += 1

            if no_new_content_count >= max_no_content_count:
                print(f"[{datetime.now()}] 无新内容，已停止读取文件。最后读取的行数位置是：{last_position}")
                break

            time.sleep(interval)
        except Exception as e:
            print(f"[{datetime.now()}] 读取文件出错：{e}")
            time.sleep(interval)

    return last_position


if __name__ == '__main__':
    path = r"D:\Scrapy\.A-Pictures_Crawler\flow.csv"
    last_pos = auto_read_growing_file(path, last_position=0, interval=8)
    print(f"最终已读取到的行位置：{last_pos}")
