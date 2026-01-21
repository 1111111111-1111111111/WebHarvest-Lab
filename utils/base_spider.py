from bs4 import BeautifulSoup
from config.headers import get_random_headers
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import time
import random

__all__ = ['ScrapyUrl']


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
                print(f"第{attempt + 1}次重试获取：{target_url}")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"解析出错 (尝试 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(30, 60))
        print(f"获取页面失败，已达最大重试次数: {target_url}")
        return None

    def get_soup_one(self, url=None):
        """获取渲染的HTML"""
        try:
            # 动态延迟
            time.sleep(random.uniform(1, 3))

            # 使用会话保持cookies
            resp = self.session.get(
                url,
                headers=get_random_headers(),  # 使用动态请求头
                timeout=15,
                verify=False,  # 禁用 SSL 验证
            )

            resp.raise_for_status()  # 检查HTTP错误
            resp.encoding = "utf-8"

            # 检查状态码
            if resp.status_code != 200:
                print(f"状态码异常: {resp.status_code}")
                return None
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup
        except requests.exceptions.ConnectionError as e:
            print(f"连接被服务器拒绝: {e}")
            return None
        except Exception as e:
            print(f"get_soup时出现错误: {e}")
            return None

    def close(self):
        """
        关闭session，释放资源
        """
        if hasattr(self, 'session'):
            self.session.close()
