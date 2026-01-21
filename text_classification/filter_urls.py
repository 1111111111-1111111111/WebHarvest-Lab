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
            os.makedirs(dest_dir, exist_ok=True)
            dir_dest_path = os.path.dirname(dest_dir)
            if process_lock:
                with process_lock:
                    filename = os.path.basename(src_path)
                    dest_path = os.path.join(dir_dest_path, filename)

                    if os.path.exists(dest_path):
                        return True
                    shutil.move(src_path, dest_path)
                    logger.info(f'{src_path} -> {dest_path}')
                    return True
            else:
                with self.lock:
                    filename = os.path.basename(src_path)
                    dest_path = os.path.join(dir_dest_path, filename)

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
            if response.status_code == 403:
                result['action'] = 'move_error'
                return result
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
            time.sleep(random.uniform(2, 3))
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and hasattr(e.response, 'status_code') and e.response.status_code == 403:
                result['action'] = 'move_error'
            else:
                logger.warning(f'请求失败{url}：{e}')
                result['action'] = 'error'
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
            already_read = self.read_txt(txt_path)
            if any(re.search(re.escape(domain), url) for url in already_read):
                self.move_file(filepath, os.path.join(base_path, 'already_read'), process_lock)
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
                        elif result['action'] == 'move_error':
                            error_path = os.path.join(base_path, 'error_path')
                            self.move_file(filepath, error_path, process_lock)
                            return True
                        elif result['action'] == 'success':
                            # 写入成功URL
                            self.write_txt(txt_path, result['tmp_url'])
                            logger.info(f'{result["new_domain"]} <- {result["url"]}')
                            # 移动文件到已处理
                            self.move_file(filepath, os.path.join(base_path, 'already_read'), process_lock)
                            return True
                        elif result['action'] == 'move_other':
                            # 移动到其他目录
                            other_path = os.path.join(base_path, 'others')
                            self.move_file(filepath, other_path, process_lock)
                            logger.info(f'{result["url"]} -> 其它')
                            return True
                        elif result['action'] == 'error':
                            # 发生错误，停止处理该文件
                            error_path = os.path.join(base_path, 'error_path')
                            self.move_file(filepath, error_path, process_lock)
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

    # 使用进程池处理文件
    with ProcessPoolExecutor(max_workers=min(multiprocessing.cpu_count(), len(files))) as executor:
        # 使用偏函数固定参数
        process_func = partial(
            process_file_wrapper,
            txt_path=txt_path,
            base_path=base_path,
            max_workers=max_workers // multiprocessing.cpu_count(),  # 合理分配线程数
            process_lock=process_lock
        )

        futures = []
        for filepath in files:
            future = executor.submit(process_func, filepath)
            futures.append(future)

        completed_count = 0
        for future in as_completed(futures):
            try:
                success = future.result()
                completed_count += 1
                logger.info(f'已完成 {completed_count}/{len(files)}个文件')
            except Exception as e:
                logger.error(f'处理文件失败：{e}')

    logger.info(f'所有文件处理完成')


def deal_folder():
    """主处理函数"""
    folder_path = r"D:\URL\越南语\渔业\other_domains2"
    txt_path = r'D:\Scrapy\A-already_read\A-already_read.txt'

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


# import logging
# import random
# import time
# import requests
# import os
# import pandas as pd
# from config.headers import HEADERS
# from urllib.parse import urlparse
# import shutil
# from bs4 import BeautifulSoup
# from tools.classificate_domain import AgricultureClassifier
# import re
# import threading
# from concurrent.futures import ThreadPoolExecutor,as_completed,ProcessPoolExecutor
# import multiprocessing
#
#
# logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
# class URLProcessor:
#     def __init__(self,max_workers=10):
#         self.max_workers = max_workers
#         self.classifier  = AgricultureClassifier()
#         self.session = requests.Session()
#         self.already_read_urls = set()
#         self.lock = threading.Lock()
#
#     @staticmethod
#     def read_txt(path):
#         """读取文本文件"""
#         try:
#             df = pd.read_csv(path, header=None,on_bad_lines='skip')
#             return set(df[0].astype(str).tolist()) if not df.emppty else set()
#         except Exception as e:
#             logger.error(f'读取文件失败 {path}:{e}')
#             return set()
#
#     @staticmethod
#     def write_txt(path, url,mode='a'):
#         """写入文本文件"""
#         try:
#             df = pd.DataFrame([url])
#             df.to_csv(path, mode=mode,index=False, header=False)
#             logger.info(f'{url} 已追加到 {path}')
#         except Exception as e:
#             logger.error(f'写入文件失败{path}:{e}')
#
#
#     def move_file(self,src_path:str, dest_dir:str):
#         """移动文件（线程安全）"""
#         with self.lock:
#             try:
#                 os.makedirs(dest_dir,exist_ok=True)
#                 filename = os.path.basename(src_path)
#                 dest_path = os.path.join(dest_dir,filename)
#
#                 # 如果目标文件已经存在，则不处理
#                 if os.path.exists(dest_path):
#                     return True
#                 shutil.move(src_path,dest_path)
#                 logger.info(f'{src_path} -> {dest_path}')
#                 return True
#             except Exception as e:
#                 logger.error(f'移动文件失败{src_path}：{e}')
#                 return False
#
#     def process_url(self,url:str,domain:str,filepath:str) -> dict:
#         """处理单个URL"""
#         result = {
#             'url':url,
#             'domain':domain,
#             'filepath':filepath,
#             'action':'continue',
#             'new_domain':None
#         }
#         try:
#             # 检查域名
#             parsed = urlparse(url)
#             if '.vn' not in parsed.netloc:
#                 result['action'] = 'delete_file'
#                 return result
#             # 发送请求
#             response = self.session.get(url,headers=HEADERS,timeout=10)
#             if response.status_code == 403:
#                 result['action'] = 'move_error'
#                 return result
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.text,'html.parser')
#                 text_content = soup.get_text(strip=True)
#
#                 # 分类
#                 classification_result = self.classifier.classify(text_content,content="")
#                 if classification_result.domain_name != '其它':
#                     tmp_url = f'{parsed.scheme}://{parsed.netloc}/'
#                     result['action'] = 'success'
#                     result['new_domain'] = classification_result.domain_name
#                     result['tmp_url'] = tmp_url
#                 else:
#                     result['action']= 'move_other'
#             time.sleep(random.uniform(2,3))
#         except requests.exceptions.RequestException as e:
#             if hasattr(e.response,'status_code') and e.response.status_code==403:
#                 result['action'] = 'move_error'
#             else:
#                 logger.warning(f'请求失败{url}：{e}')
#                 result['action'] = 'error'
#         except Exception as e:
#             logger.error(f'处理URL失败{url}:{e}')
#             result['action'] = 'error'
#         return result
#
#     def process_file(self,filepath:str,txt_path:str,base_path:str) -> bool:
#         """处理单个文件"""
#         if not os.path.exists(filepath) or os.path.getsize(filepath)==0:
#             logger.warning(f'文件为空或不存在：{filepath}')
#             return False
#         try:
#             # 读取文件中的URL
#             df = pd.read_csv(filepath,header=None,on_bad_lines='skip')
#             if df.empty:
#                 logger.warning(f'CSV文件为空：{filepath}')
#                 return False
#             urls = df[0].astype(str).tolist()
#             domain = os.path.basename(filepath).strip('_urls.txt').replace('_','.')
#             #检查是否已处理
#             already_read = self.read_txt(txt_path)
#             if any(re.search(re.escape(domain),url) for url in already_read):
#                 self.move_file(filepath,os.path.join(base_path,'already_read'))
#                 return True
#             logger.info(f'处理文件：{filepath},域名：{domain},URL数量：{len(urls)}')
#
#             # 使用线程池处理URL
#             with ThreadPoolExecutor(max_workers=min(self.max_workers,len(urls))) as executor:
#                 future_to_url = {
#                     executor.submit(self.process_url,url,domain,filepath):url
#                     for url in urls
#                 }
#                 for future in as_completed(future_to_url):
#                     try:
#                         result = future.result()
#                         if result['action'] == 'delete_file':
#                             os.remove(filepath)
#                             logger.info(f'已删除{filepath}')
#                             return True
#                         elif result['action'] == 'move_error':
#                             error_path = os.path.join(base_path,'error_path')
#                             self.move_file(filepath,error_path)
#                             return True
#                         elif result['action'] == 'success':
#                             # 写入成功URL
#                             self.write_txt(txt_path,result['tmp_url'])
#                             logger.info(f'{result['new_domain']} <- {result['url']}')
#                             # 移动文件到已处理
#                             self.move_file(filepath,os.path.join(base_path,'already_read'))
#                             return True
#                         elif result['action'] == 'move_other':
#                             # 移动到其他目录
#                             other_path = os.path.join(base_path,'others')
#                             self.move_file(filepath,other_path)
#                             logger.info(f'{result['url']} -> 其它')
#                             return True
#                         elif result['action'] =='error':
#                             # 发生错误，停止处理该文件
#                             error_path = os.path.join(base_path,'error_path')
#                             self.move_file(filepath,error_path)
#                             return True
#                     except Exception as e:
#                         logger.error(f'处理结果失败：{e}')
#                         continue
#             return False
#         except Exception as e:
#             logger.error(f'处理文件失败：{e}')
#             return False
#
#     def process_folder_parallel(self,base_path:str,txt_path:str):
#         """并行处理文件夹中的所有文件"""
#         files = []
#         for file in os.listdir(base_path):
#             filepath = os.path.join(base_path,file)
#             if file.endswith('.txt') and os.path.isfile(filepath):
#                 files.append(filepath)
#         logger.info(f'找到{len(files)}个文件需要处理')
#         with ProcessPoolExecutor(max_workers=min(multiprocessing.cpu_count(),len(files))) as process_executor:
#             # 使用偏函数固定参数
#             from functools import partial
#             process_func = partial(self._process_file_wrapper,txt_path=txt_path,base_path=base_path)
#             futures = []
#             for filepath in files:
#                 future = process_executor.submit(process_func,filepath)
#                 futures.append(future)
#             completed_count = 0
#             for future in as_completed(futures):
#                 try:
#                     success = future.result()
#                     if success:
#                         completed_count += 1
#                         logger.info(f'已完成 {completed_count}/{len(files)}个文件')
#                 except Exception  as e:
#                     logger.error(f'处理文件失败：{e}')
#         logger.info(f'所有文件处理完成')
#     def _process_file_wrapper(self,filepath,txt_path,base_path):
#         """包装函数，用于进程池中创建新的处理器实例"""
#         processor = URLProcessor(max_workers=self.max_workers)
#         return processor.process_file(filepath,txt_path,base_path)
# def deal_folder():
#     """主处理函数"""
#     path = r"D:\URL\越南语\渔业\other_domains1"
#     txt_path = r'D:\Scrapy\A-already_read\A-already_read.txt'
#     # 处理器
#     processor = URLProcessor(max_workers=12) # 可以根据需要调整线程数
#     # 并行处理
#     processor.process_folder_parallel(path,txt_path)
#
# def main():
#     start_time = time.time()
#     try:
#         deal_folder()
#     except KeyboardInterrupt:
#         logging.info('用户终端处理')
#     except Exception as e:
#         logger.error(f'处理过程发生错误：{e}')
#     finally:
#         end_time = time.time()
#         logger.info(f'总耗时：{end_time - start_time:.2f}秒')
#
# if __name__ == '__main__':
#     main()
