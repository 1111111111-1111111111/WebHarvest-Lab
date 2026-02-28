"""
Function: 从文件夹内选择符合农业十大领域的URL
author:Li
time: 2026-01-16
"""
import logging
import random
import time
import requests
import os
import pandas as pd
from config.headers import HEADERS
from urllib.parse import urlparse
import shutil
from bs4 import BeautifulSoup
from tools.classificate_domain import AgricultureClassifier
import re
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed,ThreadPoolExecutor
from functools import partial
import threading


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class URLProcessor:
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        # 不再在初始化时创建共享资源
        self.session = None
        self.classifier = None
        self.lock = None
        self.already_read_urls = None

    def _init_processor(self):
        """初始化处理器实例（每个进程单独调用）"""
        self.session = requests.Session()
        self.classifier = AgricultureClassifier()
        self.already_read_urls = set()
        self.lock = threading.Lock()  # 线程锁，用于线程池内部同步

    @staticmethod
    def read_txt(path):
        """读取文本文件"""
        try:
            df = pd.read_csv(path, header=None, on_bad_lines='skip')
            return set(df[0].astype(str).tolist()) if not df.empty else set()
        except Exception as e:
            logger.error(f'读取文件失败 {path}:{e}')
            return set()

    @staticmethod
    def write_txt(path, url, mode='a'):
        """写入文本文件"""
        try:
            df = pd.DataFrame([url])
            df.to_csv(path, mode=mode, index=False, header=False)
            logger.info(f'{url} 已追加到 {path}')
        except Exception as e:
            logger.error(f'写入文件失败{path}:{e}')

    def move_file(self, src_path: str, dest_dir: str, process_lock=None):
        """移动文件（线程安全，支持进程锁）"""
        try:
            dest_dir_path = os.path.dirname(dest_dir)
            os.makedirs(dest_dir_path, exist_ok=True)
            if process_lock:
                with process_lock:
                    filename = os.path.basename(src_path)
                    dest_path = os.path.join(dest_dir_path, filename)

                    if os.path.exists(dest_path):
                        return True
                    shutil.move(src_path, dest_path)
                    logger.info(f'{src_path} -> {dest_path}')
                    return True
            else:
                with self.lock:
                    filename = os.path.basename(src_path)
                    dest_path = os.path.join(dest_dir_path, filename)

                    if os.path.exists(dest_path):
                        return True
                    shutil.move(src_path, dest_path)
                    logger.info(f'{src_path} -> {dest_path}')
                    return True
        except Exception as e:
            logger.error(f'移动文件失败{src_path}：{e}')
            return False

    def process_url(self, url: str, domain: str, filepath: str) -> dict:
        """处理单个URL"""

        result = {
            'url': url,
            'domain': domain,
            'filepath': filepath,
            'action': 'continue',
            'new_domain': None
        }
        try:
            # 检查域名
            parsed = urlparse(url)
            if '.vn' not in parsed.netloc:
                result['action'] = 'delete_file'
                return result
            # 发送请求
            response = self.session.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = soup.get_text(strip=True)
                # 分类
                classification_result = self.classifier.classify(text_content, content="")
                if classification_result.domain_name != '其它':
                    tmp_url = f'{parsed.scheme}://{parsed.netloc}/'
                    result['action'] = 'success'
                    result['new_domain'] = classification_result.domain_name
                    result['tmp_url'] = tmp_url
                else:
                    result['action'] = 'move_other'
            return result
        except Exception as e:
            logger.error(f'处理URL失败{url}:{e}')
            result['action'] = 'error'
        return result

    def process_file(self, filepath: str, txt_path: str, base_path: str, process_lock=None) -> bool:
        """处理单个文件"""
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            logger.warning(f'文件为空或不存在：{filepath}')
            return False

        # 延迟初始化
        if self.session is None:
            self._init_processor()

        try:
            # 读取文件中的URL
            df = pd.read_csv(filepath, header=None, on_bad_lines='skip')
            if df.empty:
                logger.warning(f'CSV文件为空：{filepath}')
                return False
            urls = df[0].astype(str).tolist()
            domain = os.path.basename(filepath).strip('_urls.txt').replace('_', '.')

            # 检查是否已处理
            already_read = set(self.read_txt(txt_path))
            parse = urlparse([url for url in already_read][0])
            tmp_url = f'{parse.scheme}://{parse.netloc}'
            already_read.update({tmp_url})
            if any(re.search(re.escape(domain), url) for url in already_read):
                self.move_file(filepath, os.path.join(base_path, 'already_read'), process_lock)
                logger.info(f'{filepath}已存在')
                return True

            logger.info(f'处理文件：{filepath}, 域名：{domain}, URL数量：{len(urls)}')

            # 使用线程池处理URL
            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(urls))) as executor:
                future_to_url = {
                    executor.submit(self.process_url, url, domain, filepath): url
                    for url in urls
                }

                for future in as_completed(future_to_url):
                    try:
                        result = future.result()
                        if result['action'] == 'delete_file':
                            os.remove(filepath)
                            logger.info(f'已删除{filepath}')
                            return True
                        elif result['action'] == 'error':
                            error_path = os.path.join(base_path, 'error_path')
                            self.move_file(filepath, error_path, process_lock)
                            return True
                        elif result['action'] == 'success':
                            # 写入成功URL
                            self.write_txt(txt_path, result['url'])
                            logger.info(f'{txt_path} <- {result["url"]}')
                            # 移动文件到已处理
                            a_p = os.path.join(base_path, 'already_read')
                            self.move_file(filepath, a_p, process_lock)
                            return True
                        elif result['action'] == 'move_other':
                            # 移动到其他目录
                            other_path = os.path.join(base_path, 'others')
                            self.move_file(filepath, other_path, process_lock)
                            logger.info(f'{result["url"]} -> 其它')
                            return True
                    except Exception as e:
                        logger.error(f'处理结果失败：{e}')
                        continue
            return False
        except Exception as e:
            logger.error(f'处理文件失败：{e}')
            return False


def process_file_wrapper(filepath, txt_path, base_path, max_workers, process_lock):
    """包装函数，用于进程池中创建新的处理器实例"""
    processor = URLProcessor(max_workers=max_workers)
    return processor.process_file(filepath, txt_path, base_path, process_lock)


def process_folder_parallel(base_path: str, txt_path: str, max_workers=12):
    """并行处理文件夹中的所有文件"""
    files = []
    for file in os.listdir(base_path):
        filepath = os.path.join(base_path, file)
        if file.endswith('.txt') and os.path.isfile(filepath):
            files.append(filepath)

    logger.info(f'找到{len(files)}个文件需要处理')

    # 创建进程锁
    manager = multiprocessing.Manager()
    process_lock = manager.Lock()

    # 使用进程池分批次处理文件
    batch_size = 100
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        with ProcessPoolExecutor(max_workers=min(multiprocessing.cpu_count(), len(batch))) as executor:
            # 使用偏函数固定参数
            process_func = partial(
                process_file_wrapper,
                txt_path=txt_path,
                base_path=base_path,
                max_workers=max_workers,  # 合理分配线程数
                process_lock=process_lock
            )

            futures = []
            for filepath in batch:
                future = executor.submit(process_func, filepath)
                futures.append(future)

            completed_count = 0
            for future in as_completed(futures):
                try:
                    success = future.result()
                    completed_count += 1
                    logger.info(f'已完成 {completed_count}/{len(batch)}个文件')
                except Exception as e:
                    logger.error(f'处理文件失败：{e}')
        logger.info(f'已完成 {i // batch_size}/{len(files) //batch_size}批次')
    logger.info(f'所有文件处理完成')


def deal_folder():
    """主处理函数"""
    folder_path = r"D:\URL\英日西阿特定领域采集\英语\医疗\other_domains"
    txt_path = r'D:\Scrapy\A-already_read\already_read.txt'

    # 并行处理
    process_folder_parallel(folder_path, txt_path, max_workers=12)


def main():
    start_time = time.time()
    try:
        deal_folder()
    except KeyboardInterrupt:
        logger.info('用户中断处理')
    except Exception as e:
        logger.error(f'处理过程发生错误：{e}')
    finally:
        end_time = time.time()
        logger.info(f'总耗时：{end_time - start_time:.2f}秒')


if __name__ == '__main__':
    # 设置多进程启动方式为spawn，避免Windows平台的问题
    multiprocessing.set_start_method('spawn', force=True)
    main()

