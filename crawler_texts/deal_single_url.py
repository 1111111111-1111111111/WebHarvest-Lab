import os
from bs4 import BeautifulSoup
from config.headers import HEADERS
from utils.file_io import DealFile
import uuid
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
from tools.pdf import PdfDownloader

pdf = PdfDownloader()
dealfile = DealFile()
cleaned_urls = set()


class ScrapyUrl:
    def __init__(self, url):
        self.url = url
        self.dic = {}
        # 创建带重试机制的会话
        self.session = requests.Session()

    def get_soup(self, url=None):
        """增强行为模拟的请求方法"""
        target_url = url if url is not None else self.url
        max_retries = 3  # 重试次数
        for attempt in range(max_retries):
            try:
                soup = self.get_soup_one(target_url)
                if soup:
                    return soup
                print(f"【ERROR】 第{attempt + 1}次重试获取：{target_url}")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"【ERROR】 解析出错 (尝试 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(30, 60))
        print(f"【ERROR】 获取页面失败，已达最大重试次数: {target_url}")
        return None

    def get_soup_one(self, url=None):
        """获取渲染的HTML"""
        try:
            # 动态延迟
            time.sleep(random.uniform(3, 5))

            # 使用会话保持cookies
            resp = self.session.get(
                url,
                headers=HEADERS,  # 使用动态请求头
                timeout=10,
                verify=False,  # 禁用 SSL 验证
            )

            resp.raise_for_status()  # 检查HTTP错误
            resp.encoding = "utf-8"

            # 检查状态码
            if resp.status_code != 200:
                print(f"【ERROR】 状态码异常: {resp.status_code}")
                return None
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup
        except requests.exceptions.ConnectionError as e:
            print(f"【ERROR】 连接被服务器拒绝: {e}")
            return None
        except Exception as e:
            print(f"【ERROR】 get_soup时出现错误: {e}")
            return None

    def close(self):
        """
        关闭session，释放资源
        """
        if hasattr(self, 'session'):
            self.session.close()


class ScraperScript(ScrapyUrl, DealFile):
    def __init__(self, url=None, base_url="", max_threads=7):
        super().__init__(url)
        self.url = url
        self.base_url = base_url
        self.max_threads = max_threads
        self.results_lock = threading.Lock()
        self.write_queue = queue.Queue(maxsize=100)
        self.batch_size = 50
        self.start_writer_thread()

    def start_writer_thread(self):
        """启动异步写入线程"""
        writer_thread = threading.Thread(target=self._async_writer, daemon=True)
        writer_thread.start()

    def _async_writer(self):
        """异步写入线程函数"""
        batch_data = []
        while True:
            try:
                data = self.write_queue.get(timeout=1)
                if data is None:  # 停止信号
                    if batch_data:
                        self._batch_write_files(batch_data)
                    break

                batch_data.append(data)
                if len(batch_data) >= self.batch_size:
                    self._batch_write_files(batch_data)
                    batch_data = []

            except queue.Empty:
                if batch_data:
                    self._batch_write_files(batch_data)
                    batch_data = []

    def _batch_write_files(self, batch_data):
        """批量写入文件"""
        for item in batch_data:

            try:
                data = {
                    "id": item["id"],
                    "url": item["url"],
                    "language": item["language"],
                    "labels": item["labels"],
                    "title": item["title"],
                    "content": item["content"],
                }
                self.write_json(f'{item["id"]}.json', item["path"], data)
            except Exception as e:
                print(f"【ERROR】 批量写入失败: {e}")

    # 修改 process_urls 方法，使用已导入的 ThreadPoolExecutor
    def process_urls(self, all_urls):
        all_url = set(all_urls.split("\n"))
        for url in all_url.copy():
            if not url or url.endswith(".jpg"):
                all_url.remove(url)
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:  # 使用已导入的类
            futures = {
                executor.submit(self._download_content_page_isolated, url): url
                for url in all_url
            }

            completed = 0
            failed = 0
            total = len(futures)

            for future in as_completed(futures):  # 使用已导入的 as_completed
                url = futures[future]
                try:
                    result = future.result()
                    if result:
                        completed += 1
                        print(f"【INFO】 期刊进度: {completed}/{total} - 已完成: {url}")
                    else:
                        failed += 1
                        print(f"【ERROR】 第{failed}个期刊处理失败 {url}")
                        self.write_txt(r"failed_VI_url.txt", r"D:\Scrapy\scripts\多语言语料文本采集\越南语URL",
                                       url + "\n", "a+")
                except Exception as e:
                    print(f"【ERROR】 期刊处理异常: {url}, 错误: {e}")

    def _download_content_page_isolated(self, content_url):
        """独立的内容页下载方法"""
        print(f"【INFO】 提取文章内容:{content_url}")
        if content_url.endswith(('.pdf','.doc','.rar','xlsx')):
            res = pdf.download_pdf(content_url)
            return res

        soup = self.get_soup(content_url)
        if not soup:
            print(f"【ERROR】 无法获取内容页: {content_url}")
            return None

        try:
            content_text, length = self.extract_content_text(soup,content_url)
            content_title = self.extract_content_title(soup,content_url)

            if not content_text or not content_title:  # 提前过滤短内容  or length < 200
                return None
            id = str(uuid.uuid4())
            result = {
                "id": id,
                "url": content_url,
                "language": "vi",
                "labels": "news",
                "title": content_title,
                "content": content_text,
            }

            # 初始化分类器
            from tools.classificate_domain import AgricultureClassifier
            classifier = AgricultureClassifier()
            classifier_result = classifier.classify(content_title, content_text)

            import hashlib
            md5 = hashlib.md5()

            path = fr"D:\DATA\多语言语料文本采集\越南语\{classifier_result.domain_name}" # {classifier_result.domain_name}
            os.makedirs(path, exist_ok=True)
            result["path"] = path

            self.write_queue.put(result)  # 使用异步写入
            return result
        except Exception as e:
            print(f"【ERROR】 处理内容页异常: {e}")
            return None

    def extract_content_title(self, soup,url):
        """提取内容标题"""
        try:
            title_tag = soup.find("h1",{'class':'title-detail'})
            if not title_tag:
                title_tag = soup.find("h1", {'class': 'head_title'})
                if not title_tag:
                    print(f'【ERROR】无标题 -> {url} ')
                    return None

            print(title_tag)
            title = title_tag.text.strip()
            return title
        except Exception as e:
            print(f"【ERROR】 解析标题失败: {e} -> {url}")

    def extract_content_text(self, soup,url):
        """提取正文内容"""
        try:
            content_parts = ""
            intro_div = soup.find("article", {"id": "fck_detail_gallery"})  # vc_column-inner
            if intro_div:
                content_parts += intro_div.get_text(strip=True)

            intro_div = soup.find("div", {"id": "content"})  # vc_column-inner
            if intro_div:
                content_parts += intro_div.get_text(strip=True)

            intro_div = soup.find('div',{'class':'td-post-content tagdiv-type'})
            if intro_div:
                content_parts += intro_div.get_text(strip=True)

            if content_parts:
                print(f"【INFO】 文章总字数是：{len(content_parts)} -> {url}")
                return content_parts, len(content_parts)
            else:
                print(f'【ERROR】 无法获取文章内容 -> {url}')
                return None, 0

        except Exception as e:
            print(f"【ERROR】 提取正文内容失败: {e}")
            return None, 0


def auto_read_growing_file(self, file_path, last_position=0, interval=8):
    """
    每 5 s 自动读取正在增长的文件内容

    Args:
        file_path:
        interval:

    """
    no_new_content_count = 0
    max_no_content_count = 3  # 最大无新内容次数

    while True:
        try:
            file_size = os.path.getsize(file_path)
            if file_size > last_position:
                with open(file_path, "r", encoding="utf-8") as f:
                    f.seek(last_position)
                    new_content = f.read()
                    last_position = f.tell()
                    if new_content:
                        print(f"【INFO】 读取到新内容：{len((new_content))} 字符")
                        self.process_urls(new_content)  # 处理新内容
                        no_new_content_count = 0
                    else:
                        no_new_content_count += 1
            else:
                no_new_content_count += 1

            if no_new_content_count >= max_no_content_count:
                print(f"【INFO】 {datetime.now()}无新内容，已停止读取文件,最后读取的文件位置是：{last_position}")
                break

            time.sleep(interval)
        except Exception as e:
            print(f"【ERROR】 读取文件出错：{e}")
            time.sleep(interval)

    return last_position


if __name__ == "__main__":
    scrapy = ScraperScript("")
    path = r"D:\Scrapy\scripts\多语言语料文本采集\越南语URL\vi_URL1_1.txt"
    auto_read_growing_file(scrapy, path, last_position=0)
    scrapy.close()
