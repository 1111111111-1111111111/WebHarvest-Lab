from bs4 import BeautifulSoup
from config.headers import HEADERS
import re
import asyncio
import aiohttp
import logging
import os
import time
import random
import hashlib
import pandas as pd
from urllib.parse import urlparse
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 文件处理器
file_handler = logging.FileHandler('D://pictures_log.log', mode='a', encoding='utf-8')

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)

# 设置格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s -%(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

console_handler.setLevel(logging.INFO)

# 添加到logger中
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 避免重复日志
logger.propagate = False


class MultiLevelAsyncCrawler:
    def __init__(self, max_concurrent_level1=20, max_concurrent_level2=50, timeout=30, retry_times=2,
                 save_path='./download'):
        self.max_concurrent_level1 = max_concurrent_level1
        self.max_concurrent_level2 = max_concurrent_level2
        self.timeout = timeout
        self.retry_times = retry_times
        self.save_path = save_path

        # 创建保存目录
        os.makedirs(self.save_path, exist_ok=True)

        # 统计信息
        self.stats = {
            'level1_total': 0,
            'level1_success': 0,
            'level2_total': 0,
            'level2_success': 0,
            'images_found': 0,
            'images_saved': 0,  # 添加images_saved字段
            'start_time': None,
            'end_time': None
        }

        # 添加防反爬相关属性
        self.request_count = 0  # 请求计数器
        self.domain_delays = {}  # 域名延迟记录
        self.last_request_time = {}  # 每个域名的最后请求时间
        self.min_delay = 1.0  # 最小延迟（秒）
        self.max_delay = 3.0  # 最大延迟（秒）


    def _get_domain(self, url):
        """提取域名"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"

    async def _random_delay(self, url):
        """随机延迟控制"""
        domain = self._get_domain(url)

        # 检查是否需要延迟
        current_time = time.time()
        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            if elapsed < self.min_delay:
                # 随机延迟
                delay_time = random.uniform(self.min_delay - elapsed, self.max_delay - elapsed)
                print(f"为域名 {domain} 添加延迟: {delay_time:.2f}秒")
                await asyncio.sleep(delay_time)

        # 更新最后请求时间
        self.last_request_time[domain] = time.time()

        # 每10个请求增加一次较长的随机延迟
        self.request_count += 1
        if self.request_count % 10 == 0:
            long_delay = random.uniform(2.0, 5.0)
            print(f"每10个请求后的随机长延迟: {long_delay:.2f}秒")
            await asyncio.sleep(long_delay)

    async def fetch_image_url(self, session, url):  # 修改方法名，与调用处保持一致
        """提取图片，保存到指定路径"""
        try:
            # 添加延迟控制
            await self._random_delay(url)

            async with session.get(url, timeout=self.timeout, headers=HEADERS) as response:
                if response.status != 200:
                    return {
                        'url': url,
                        'image_url': None,
                        'status': response.status,
                        'success': False,
                        'error': f'HTTP {response.status}'
                    }
                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")
                scripts_tag = soup.find_all("script")

                image_url = None  # 初始化变量
                for script in scripts_tag:
                    if "window.bigPicture" in str(script):
                        bigPicture = re.findall(r"window.bigPicture=\"(.*?)\"", script.text)
                        if bigPicture:
                            image_url = bigPicture[0]
                            break  # 找到后跳出循环

                if image_url:
                    return {
                        'url': url,
                        'image_url': image_url,
                        'status': 200,
                        'success': True,
                        'error': None
                    }
                else:
                    return {
                        'url': url,
                        'image_url': None,
                        'status': 200,
                        'success': False,
                        'error': '未找到图片链接'
                    }
        except Exception as e:
            return {
                'url': url,
                'image_url': None,
                'status': 500,
                'success': False,
                'error': str(e)
            }

    async def fetch_single_url(self, session, url):
        """第一层级：获取页面中的所有目标URL"""
        single_urls = []
        try:
            # 添加延迟控制
            await self._random_delay(url)

            async with session.get(url, timeout=self.timeout, headers=HEADERS) as response:
                if response.status != 200:
                    print(f'第一层请求失败：{url},状态码:{response.status}')
                    return single_urls

                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")

                ul_tag = soup.find("ul", {'class': 'temp-tag-list'})
                if not ul_tag:
                    print(f'页面 {url} 不存在图片模版容器')
                    return single_urls

                for li_tag in ul_tag.find_all("li"):
                    a_tag = li_tag.find("a")
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        single_urls.append(href)
                logger.info(f'从{url}提取到{len(single_urls)}个目标URL')
                return single_urls
        except Exception as e:
            print(f'获取单个URL内容失败 {e}')
            return single_urls  # 保持返回类型一致

    async def process_batch_level1(self, urls):
        """并发处理第一层级URL"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent_level1)

        async with aiohttp.ClientSession(connector=connector, headers=HEADERS) as session:
            tasks = [self.fetch_single_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=False)

            # 合并所有提取的URL
            all_single_urls = []
            for url, result in zip(urls, results):
                if result and isinstance(result, list):  # 检查返回的是列表
                    all_single_urls.extend(result)
                    self.stats['level1_success'] += 1
                self.stats['level1_total'] += 1

            # 去重
            unique_urls = list(set(all_single_urls))
            logger.info(f'第一层级完成，共提取{len(unique_urls)}个唯一URL')
            return unique_urls

    async def download_image(self, session, image_info):
        """第三层：下载图片"""
        if not image_info['success'] or not image_info['image_url']:
            return {**image_info, 'downloaded': False, 'save_path': None}  # 修正拼写错误

        try:
            image_url = image_info['image_url']

            async with session.get(image_url, timeout=self.timeout) as response:
                if response.status != 200:
                    pd.DataFrame([image_info]).to_csv('failed.csv', mode='a', index=False, header=False)
                    return {
                        **image_info,
                        'downloaded': False,
                        'save_path': None,
                        'error': f'图片下载失败：HTTP {response.status}'
                    }

                # 读取内容
                content = await response.read()  # 修正：需要await读取内容

                # 生成文件名
                filename = hashlib.md5(content).hexdigest()
                content_type = response.headers.get('Content-Type', '')
                if '/' in content_type:
                    extension = content_type.lower().split('/')[1]
                    # 处理可能的参数，如 'image/jpeg; charset=utf-8'
                    if ';' in extension:
                        extension = extension.split(';')[0]
                else:
                    extension = 'jpg'  # 默认扩展名

                save_path = os.path.join(self.save_path, f'{filename}.{extension}')
                with open(save_path, 'wb') as f:
                    f.write(content)
                print(f"{filename} 图片保存成功")

                return {
                    **image_info,
                    'downloaded': True,
                    'save_path': save_path,
                    'file_size': len(content)
                }

        except Exception as e:
            pd.DataFrame([image_info]).to_csv('failed.csv', mode='a', index=False, header=False)
            return {
                **image_info,
                'downloaded': False,
                'save_path': None,
                'error': str(e)
            }

    async def process_level2_and_download(self, single_urls):
        """并发处理第二层级URL并下载图片"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent_level2)

        async with aiohttp.ClientSession(connector=connector, headers=HEADERS) as session:
            print(f'开始处理第二层级：共{len(single_urls)}个URL')

            batch_size = 100
            all_results = []

            # 计算批次总数
            total_batches = (len(single_urls) - 1) // batch_size + 1

            for i in range(0, len(single_urls), batch_size):
                batch_urls = single_urls[i:i + batch_size]
                batch_num = i // batch_size + 1
                print(f'开始处理第二层级批次{batch_num}/{total_batches}')

                # 获取图片URL
                image_tasks = [self.fetch_image_url(session, url) for url in batch_urls]  # 修正方法名
                image_results = await asyncio.gather(*image_tasks)

                # 过滤出成功的图片URL
                valid_images = [r for r in image_results if r['success']]

                # 保存图片URL到CSV
                if valid_images:
                    image_urls = [r['image_url'] for r in valid_images]
                    df_batch = pd.DataFrame({'image_urls': image_urls})
                    if i == 0:
                        df_batch.to_csv('image_urls.csv', index=False, header=True, mode='w', encoding='utf-8-sig')
                    else:
                        df_batch.to_csv('image_urls.csv', index=False, header=False, mode='a', encoding='utf-8-sig')

                # 并发下载图片
                download_tasks = [self.download_image(session, img_info) for img_info in valid_images]
                download_results = await asyncio.gather(*download_tasks)

                all_results.extend(download_results)

                # 更新统计
                self.stats['level2_total'] += len(batch_urls)
                self.stats['images_found'] += len(valid_images)
                self.stats['images_saved'] += sum(1 for r in download_results if r['downloaded'])  # 修正字段名

                # 批次间短暂停顿
                if i + batch_size < len(single_urls):
                    await asyncio.sleep(1)

            return all_results

    async def run(self, start_urls):
        """运行整个爬虫流程"""
        self.stats['start_time'] = time.time()  # 添加开始时间

        try:
            print(f'开始共 {len(start_urls)}个起始URL')

            # 第一层：获取所有目标URL
            single_urls = await self.process_batch_level1(start_urls)
            if not single_urls:
                logger.warning('未提取到任何目标URL,程序结束')
                return {'success': False, 'results': [], 'stats': self.stats}

            # 保存第一层结果
            if single_urls:
                df = pd.DataFrame({'urls': single_urls})
                df.to_csv('ProcessOn.csv', header=True, mode='w', index=False, encoding='utf-8-sig')

            # 第二层：处理第二层级URL
            print(f'开始第二层级处理，共{len(single_urls)}个目标URL')
            results = await self.process_level2_and_download(single_urls)

            # 计算时间
            self.stats['end_time'] = time.time()  # 添加结束时间
            elapsed = self.stats['end_time'] - self.stats['start_time']

            # 打印统计信息
            logger.info('爬虫执行完成！')
            logger.info(f'总耗时：{elapsed:.2f}秒')
            logger.info(f"第一层级：{self.stats['level1_success']}/{self.stats['level1_total']}成功")  # 修正字段名
            logger.info(f"第二层级：{self.stats['level2_total']}个URL处理完成")
            logger.info(f'发现图片：{self.stats['images_found']}张')
            logger.info(f'保存图片：{self.stats['images_saved']}张')  # 添加保存图片统计

            return {
                'success': True,
                'results': results,
                'stats': self.stats,
                'total_urls': len(single_urls),
                'total_images': self.stats['images_saved']
            }

        except Exception as e:
            print(f'爬虫执行失败：{e}')
            self.stats['end_time'] = time.time()  # 异常时也记录结束时间
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }

class ProcessLog:
    def __init__(self):
        df = pd.read_csv('num.txt',header=None)
        self.alread_num = df.iloc[:,0].to_list()

    def get_num(self,log_path):
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                pass
        try:
            df = pd.read_csv(log_path, header=None,on_bad_lines='skip')
        except pd.errors.EmptyDataError:
            return self.alread_num

        log_info = df.iloc[:, 1].to_list()
        log_list = []
        for i in log_info:
            if '提取到60个目标URL' in i:
                pattern = r"从https://www.processon.com/template/flow/talent_page(.*?)提取到"
                num = re.findall(pattern, i)
                if not len(num):
                    continue
                log_list.append(int(num[0]))
        if log_list == []:
            return self.alread_num

        for i in log_list:
            if i in self.alread_num:
                self.alread_num.remove(i)
        print(len(log_list))
        print(len(self.alread_num))
        logger.info(self.alread_num)
        df = pd.DataFrame(self.alread_num)
        df.to_csv('num.txt', index=False, header=False)
        return self.alread_num

async def main():
    current_num = 0
    retries = 0
    max_retries = 3
    while True:
        all_urls = []
        #
        # 已读取：热门\推荐\克隆最多\最新发布\达人
        dl = ProcessLog()
        log_path = r"D://pictures_log.log"
        no_num = dl.get_num(log_path)
        if current_num != no_num:
            current_num = no_num
            print(f'当前爬取数字长度是{len(no_num)}')
        else:
            retries += 1
            print(f'retries: {retries}')
        if max_retries < retries:
            print('3 次重试机制全部触发，程序结束')
            break
        time.sleep(random.uniform(1,2))

        if len(no_num) == 0:
            break

        for i in no_num: # 3554
            if i == 1:
                url = r"https://www.processon.com/template/flow/talent"
            else:
                url = rf"https://www.processon.com/template/flow/talent_page{i}"
            all_urls.append(url)

        crawler = MultiLevelAsyncCrawler(
            max_concurrent_level1=20,
            max_concurrent_level2=50,
            timeout=30,
            retry_times=3,
            save_path=r'D:\DATA\DATA\Pictures\流程图'
        )

        results = await crawler.run(all_urls)

        # 打印最终结果
        if results['success']:
            print(f"\n爬虫执行成功！")
            print(f"总共处理URL：{results['total_urls']}个")
            print(f"成功下载图片：{results['total_images']}张")
        else:
            print(f"\n爬虫执行失败：{results['error']}")


if __name__ == '__main__':
    asyncio.run(main())