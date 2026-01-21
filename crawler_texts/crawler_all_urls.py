import requests
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import logging
from collections import deque
import threading
import os
import random
import urllib3
import concurrent.futures

from utils.file_io import DealFile


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class URLBatchCrawler(DealFile):
    """
    URL批量爬虫
    - 多线程爬取页面，提取符合条件的目标URL
    - 按批次将URL保存到指定文件
    """

    def __init__(self, start_url, delay=2, max_workers=20,
                 batch_size=50):
        """
        初始化爬虫

        Args:
            start_url: 起始URL

            delay: 请求延迟
            respect_robots: 是否遵守robots.txt
            batch_size: 批次大小，每批次保存的URL数量
        """
        super().__init__()
        self.start_url = start_url
        self.delay = delay
        self.batch_size = batch_size

        # 设置基础URL
        self.base_url,self.target_domain = self.get_base_url(start_url)

        self.max_workers = max_workers

        # 数据结构
        self.queue = deque()  # 待处理URL队列
        self.stack = []  # 需要递归爬取的URL栈
        self.visited = set()  # 已访问URL集合

        # 批次存储相关
        self.batch_urls = []  # 当前批次的URL
        self.batch_count = 0  # 批次计数器
        self.all_batched_urls = set()  # 统计已保存的URL
        self.batch_lock = threading.Lock()  # 批次锁
        self.url_count = 0  # 已保存的URL总数

        # 统计信息
        self.page_count = 0
        self.queue_processed = 0
        self.stack_processed = 0

        # 线程锁
        self.lock = threading.Lock()

        # User-Agent池，用于反反爬虫
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]

        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # 会话设置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; URLBatchCrawler/1.0)'
        })

        # 保存已访问的其他域名的URL
        self.other_domain_visited = set()
        # 加载已存在的URL
        self.load_existing_urls()
        # 加载已存在的其他域名的URL
        self.load_other_domain_urls()

    def get_base_url(self, url):
        """从URL中提取基础URL（协议+域名）"""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            return base_url,parsed.netloc
        except Exception as e:
            self.logger.error(f"提取基础URL失败 {url}: {e}")
            return url,urlparse(url).netloc


    def is_same_domain(self, url):
        """检查URL是否属于目标域名"""
        try:
            parsed = urlparse(url)
            return self.target_domain in parsed.netloc
        except Exception:
            return False

    def normalize_url(self, url):
        """规范化URL"""
        try:
            full_url = urljoin(self.base_url, url)
            if url.startswith(('http://', 'https://')):
                full_url = url
            elif url.startswith('/'):
                full_url = urljoin(self.base_url, url)
            elif url.startswith('//'):
                full_url = f'http:{url}'
            return full_url
        except Exception as e:
            self.logger.debug(f"URL规范化失败 {url}: {e}")
            return None

    def is_final_url(self, url):
        """判断是否为最终数据URL"""
        return re.search(self.target_domain,url) is not None

    def extract_links(self, url, html_content):
        """从HTML内容中提取链接 - 使用base_url进行规范化"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = set()
            domain_links = {}  # 用于存储不同域名的链接

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # 使用base_url进行规范化
                normalized_url = self.normalize_url(href)

                if normalized_url not in self.visited:
                    if self.is_same_domain(normalized_url):
                        links.add(normalized_url)
                    else:
                        try:
                            parsed = urlparse(normalized_url)
                            domain = parsed.netloc
                            if domain not in domain_links:
                                domain_links[domain] = []
                            domain_links[domain].append(normalized_url)
                        except Exception:
                            pass

            # 保存其他域名的链接到各自文件中
            self.save_domain_links(domain_links)

            return links

        except Exception as e:
            self.logger.error(f"提取链接失败 {url}: {e}")
            return []

    def load_other_domain_urls(self):
        """加载已存在其他域名的URL"""
        try:
            output_path = r"D:\URL\越南语\渔业\other_domains"
            if not os.path.exists(output_path):
                return

            for filename in os.listdir(output_path):
                if filename.endswith('_urls.txt'):
                    filepath = os.path.join(output_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                url = line.strip()
                                if url:
                                    self.other_domain_visited.add(url)
                    except Exception as e:
                        self.logger.error(f"加载其他域名的URL失败 {filepath}: {e}")
            self.logger.info(f"已加载其他域名的URL: {len(self.other_domain_visited)}")
        except Exception as e:
            self.logger.error(f"加载其他域名的URL失败: {e}")

    def filter_urls(self, url):
        """过滤URL"""
        domain = urlparse(url).netloc.lower()

        # 社交媒体域名检查（使用in进行子字符串匹配）
        social_domains = {
            'facebook.com', 'fb.com', 'fb.me',
            'twitter.com', 'x.com', 't.co',
            'instagram.com', 'instagr.am',
            'tiktok.com', 'tiktokv.com',
            'linkedin.com', 'lnkd.in',
            'pinterest.com', 'pin.it',
            'reddit.com', 'redd.it',
            'kaskus.co.id',
            'line.me', 'line-apps.com',
            'whatsapp.com', 'wa.me',
            'telegram.org', 't.me',
            'glassdoor.com', 'indeed.com',
            'snapchat.com', 'sc-cdn.net',
            'discord.com', 'discord.gg',
            'twitch.tv',
            'quora.com',
            'medium.com',
            'nextdoor.com',
            'youtube.com', 'youtu.be',
            "www.facebook.com","www.tiktok.com"
        }

        # 检查域名是否包含社交媒体域名
        if any(social_domain in domain for social_domain in social_domains):
            return False

        # 检查常见社交媒体子域名
        social_subdomains = ['m.facebook', 'l.facebook', 'web.facebook',
                             'mobile.twitter', 'instagram.fcgk', 'pbs.twimg']

        if any(subdomain in domain for subdomain in social_subdomains):
            return False
        return True

    def save_domain_links(self, domain_links):
        """保存不同域名的链接到对应文件中"""
        try:
            output_path = r"D:\URL\越南语\渔业\other_domains"
            os.makedirs(output_path, exist_ok=True)

            new_links_count = 0
            for domain, links in domain_links.items():
                if links:
                    # 去重处理
                    unique_links = []
                    for link in links:
                        if link not in self.other_domain_visited:
                            self.other_domain_visited.add(link)
                            if self.filter_urls(link):
                                unique_links.append(link)

                    if unique_links:
                        filename = f"{domain.replace('.', '_')}_urls.txt"
                        filepath = os.path.join(output_path, filename)

                        with open(filepath, 'a', encoding='utf-8') as f:
                            for link in unique_links:
                                f.write(link + '\n')
                        new_links_count += len(unique_links)
            if new_links_count > 0:
                self.logger.info(f"已保存 {len(domain_links)} 个其他域名的链接")

        except Exception as e:
            self.logger.error(f"保存域名链接失败: {e}")

    def load_existing_urls(self):
        """加载已存在的URL到内存集合中"""
        try:
            output_path = r"D:\Scrapy\scripts\多语言语料文本采集\越南语URL"
            filename = r"vi_URL1_1.txt"
            filepath = os.path.join(output_path, filename)

            if os.path.exists(filepath):
                existing_urls = self.read_txt(filename, output_path)
                existing_urls = set(existing_urls.split("\n"))
                with self.lock:
                    for url in existing_urls:
                        url = url.strip()
                        if url:
                            self.visited.add(url)
                self.logger.info(f"已加载 {len(existing_urls)} 个已存在的URL")
        except Exception as e:
            self.logger.error(f"加载已存在URL失败: {e}")

    def add_to_batch(self, url):
        """将URL添加到当前批次，如果批次满了则保存"""
        with self.batch_lock:
            if url not in self.batch_urls:
                self.batch_urls.append(url)
                self.url_count += 1

            # 如果批次达到指定大小，保存批次
            if len(self.batch_urls) >= self.batch_size:
                self.save_batch()

    def save_batch(self):
        """保存当前批次到文件"""
        if not self.batch_urls:
            return

        try:
            self.batch_count += 1
            # 保存批次URL到文件
            output_path = r"D:\Scrapy\scripts\多语言语料文本采集\越南语URL"
            filename = r"vi_URL1_1.txt"
            with open(os.path.join(output_path, filename), 'a', encoding='utf-8') as f:
                with self.lock:
                    for url in self.batch_urls:
                        if url not in self.all_batched_urls:
                            self.all_batched_urls.add(url)
                            f.write(url + '\n')

            self.logger.info(f"已保存批次 {self.batch_count}，包含 {len(self.batch_urls)} 个URL到 {filename}")

            # 清空当前批次
            self.batch_urls = []

        except Exception as e:
            self.logger.error(f"保存批次失败: {e}")

    def save_remaining_batch(self):
        """保存剩余的批次URL"""
        if self.batch_urls:
            self.save_batch()

    def process_page(self, url, is_final=False):
        """处理单个页面，提取链接"""
        if url in self.visited:
            return [], []

        with self.lock:
            if url in self.visited:
                return [], []
            self.visited.add(url)
            if is_final:
                self.queue_processed += 1
            else:
                self.stack_processed += 1

        self.logger.info(f"找到页面 [{'队列' if is_final else '栈'}]: {url}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 随机延迟，避免被反爬虫检测
                base_delay = self.delay + random.uniform(1, 3)
                time.sleep(base_delay * (2 ** attempt))  # 指数退避

                # 随机选择User-Agent
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
                self.session.verify = False  # 为整个session禁用SSL验证
                response = self.session.get(url, timeout=15, headers=headers, verify=False)

                # 检查是否是429或428错误
                if response.status_code in [428, 429]:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"请求过于频繁，等待后重试 ({attempt + 1}/{max_retries}): {url}")
                        time.sleep(5 * (2 ** attempt))  # 逐步增加等待时间
                        continue
                    else:
                        self.logger.error(f"多次重试后仍然被限制访问: {url}")
                        return [], []

                response.raise_for_status()

                # 提取该页面的所有链接
                links = self.extract_links(url, response.content)

                # 分类处理链接
                new_final_urls = []
                new_recursive_urls = []

                for link in links:
                    if link not in self.visited:
                        if self.is_final_url(link):
                            new_final_urls.append(link)
                            # 将符合条件的URL添加到批次中
                            self.add_to_batch(link)
                        else:
                            new_recursive_urls.append(link)

                return new_final_urls, new_recursive_urls

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"请求失败，正在重试 ({attempt + 1}/{max_retries}): {url}")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    self.logger.error(f"处理页面失败 {url}: {e}")
                    return [], []
            except Exception as e:
                self.logger.error(f"处理页面失败 {url}: {e}")
                return [], []

    def start_crawling(self):
        """开始爬取"""
        self.logger.info("开始URL批量爬取...")
        self.logger.info(f"起始URL: {self.start_url}")
        self.logger.info(f"目标域名: {self.target_domain}")
        self.logger.info(f"批次大小: {self.batch_size}")
        self.logger.info(f"基础URL: {self.base_url}")

        # 初始化：处理起始URL
        start_url_normalized = self.normalize_url(self.start_url)

        # 调试信息
        self.logger.info(f"规范化起始URL: {start_url_normalized}")
        self.logger.info(f"是否最终URL: {self.is_final_url(start_url_normalized)}")

        # 无论起始URL是什么类型，都先放入栈进行递归爬取
        if start_url_normalized not in self.visited and not start_url_normalized.endswith((".png",".jgp",".jepg")):
            self.stack.append(start_url_normalized)

        # 同时，如果它是最终URL，也添加到批次中
        if self.is_final_url(start_url_normalized) and not start_url_normalized.endswith((".png",".jgp",".jepg")):
            self.add_to_batch(start_url_normalized)

        # 使用线程池进行并发爬取
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            # 提交初始任务
            if self.queue:
                url = self.queue.popleft()
                future = executor.submit(self.process_page, url, True)
                futures[future] = (True, url)
            elif self.stack:
                url = self.stack.pop()
                future = executor.submit(self.process_page, url, False)
                futures[future] = (False, url)

            # 主循环
            while (self.queue or self.stack or futures):
                # 检查已完成的任务
                done_futures = []


                for future in list(futures.keys()):
                    if future.done():
                        done_futures.append(future)

                for future in done_futures:
                    futures.pop(future)
                    try:
                        new_final_urls, new_recursive_urls = future.result(timeout=30)

                        # 将新发现的URL添加到相应数据结构
                        with self.lock:
                            for new_url in new_final_urls:
                                if new_url not in self.visited and new_url not in self.queue:
                                    self.queue.append(new_url)
                            for new_url in new_recursive_urls:
                                if new_url not in self.visited and new_url not in self.stack:
                                    self.stack.append(new_url)

                    except Exception as e:
                        self.logger.error(f"处理任务结果失败: {e}")

                # 提交新任务
                while len(futures) < self.max_workers and (
                        self.queue or self.stack):

                    if self.queue:
                        url = self.queue.popleft()
                        future = executor.submit(self.process_page, url, True)
                        futures[future] = (True, url)
                    elif self.stack:
                        url = self.stack.pop()
                        future = executor.submit(self.process_page, url, False)
                        futures[future] = (False, url)
                    else:
                        break

                # 短暂休眠，避免CPU过度占用
                time.sleep(0.9)

            # 等待所有剩余任务完成
            for future in concurrent.futures.as_completed(futures.keys()):
                try:
                    new_final_urls, new_recursive_urls = future.result(timeout=30)

                    # 将新发现的URL添加到相应数据结构
                    with self.lock:
                        for new_url in new_final_urls:
                            if new_url not in self.visited and new_url not in self.queue:
                                self.queue.append(new_url)
                        for new_url in new_recursive_urls:
                            if new_url not in self.visited and new_url not in self.stack:
                                self.stack.append(new_url)

                except Exception as e:
                    self.logger.error(f"处理剩余任务结果失败: {e}")

        # 保存剩余的批次URL
        self.save_remaining_batch()

        # 输出统计信息
        self.logger.info("爬取完成！")
        self.logger.info(f"总处理页面数: {self.page_count}")
        self.logger.info(f"队列处理数: {self.queue_processed}")
        self.logger.info(f"已保存URL总数: {self.url_count}")
        self.logger.info(f"剩余队列URL: {len(self.queue)}")
        self.logger.info(f"批次文件数: {self.batch_count}")

    def get_statistics(self):
        """获取爬取统计信息"""
        return {
            'total_pages': self.page_count,
            'queue_processed': self.queue_processed,
            'stack_processed': self.stack_processed,
            'url_count': self.url_count,
            'queue_size': len(self.queue),
            'stack_size': len(self.stack),
            'visited_count': len(self.visited),
            'batch_count': self.batch_count
        }


# 使用示例和测试
def main():
    """使用示例"""
    # 配置参数
    config = {
        'start_url': r'https://baodongnai.com.vn/dong-nam-bo/',
        'delay': 2,
        'max_workers': 10,  # 工作线程数
        'batch_size': 100,  # 每批次保存100个URL
    }

    # 创建爬虫实例
    crawler = URLBatchCrawler(
        start_url=config['start_url'],
        delay=config['delay'],
        max_workers=config['max_workers'],
        batch_size=config['batch_size'],
    )

    # 开始爬取
    try:
        crawler.start_crawling()

        # 输出统计信息
        stats = crawler.get_statistics()
        print("\n爬取统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except KeyboardInterrupt:
        crawler.logger.info("用户中断爬取")
        # 保存剩余的批次URL
        crawler.save_remaining_batch()
    except Exception as e:
        crawler.logger.error(f"爬取过程中发生错误: {str(e)}")
        # 保存剩余的批次URL
        crawler.save_remaining_batch()


if __name__ == "__main__":
    main()
