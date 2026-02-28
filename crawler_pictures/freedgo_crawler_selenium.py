import time
import random
import asyncio
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from crawler_pictures.知乎_流程图 import download_images
import traceback

class ProxyCrawler:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    def setup_driver(self,proxy=None):
        """配置Chrome浏览器选项"""
        chrome_options = Options()

        # 无头模式（不显示浏览器窗口）
        chrome_options.add_argument('--headless')

        # 反爬虫规避
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 性能优化
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # 设置窗口大小
        chrome_options.add_argument('--window-size=1920,1080')

        # 设置用户代理
        chrome_options.add_argument(
            f'--user-agent={self.get_random_user_agent}')
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
            print(f'使用代理：{proxy}')

        # 设置ChromeDriver服务
        service = Service(executable_path=r'D:\python_pro\chromedriver\chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 添加额外的反检测参数
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)


        # 隐藏webdriver特征
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['zh-CN', 'zh', 'en']
                        });
                        window.chrome = {
                            runtime: {}
                        };
                    '''
        })
        return driver


    def wait_for_element(self,driver, by, value, timeout=10):
        """等待元素加载"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except:
            return None

    def get_random_user_agent(self):
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        return random.choice(user_agents)

    def scroll_to_load(self,driver, max_scrolls=5):
        """滚动页面以加载更多内容"""
        last_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(max_scrolls):
            # 滚动到页面底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))  # 等待内容加载

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # 没有新内容加载
            last_height = new_height


    async def crawler_main(self,url):  # session参数保留以兼容原有调用
        """使用代理爬取单个URL"""
        all_urls = []
        driver = None
        df = pd.read_csv(r"D:\proxy\proxy_pool.csv", header=None)
        proxy = df.values.tolist()
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                print(f"正在爬取: {url} (尝试 {retry_count + 1}/{max_retries})")
                driver = self.setup_driver()

                # 设置页面加载超时
                driver.set_page_load_timeout(30)

                # 加载页面
                driver.get(url)

                # 等待页面加载完成
                await asyncio.sleep(random.uniform(3, 5))

                # 等待masonry元素出现
                masonry_div = self.wait_for_element(driver, By.ID, "masonry", timeout=10)

                if not masonry_div:
                    print(f"未找到masonry元素 -> {url}")
                    # 调试：打印页面标题和URL
                    print(f"页面标题: {driver.title}")
                    print(f"当前URL: {driver.current_url}")

                    # 获取所有div的ID用于调试
                    all_divs = driver.find_elements(By.TAG_NAME, "div")
                    div_ids = [div.get_attribute("id") for div in all_divs if div.get_attribute("id")]
                    print(f"页面中的div IDs: {div_ids}")

                    return all_urls

                # 滚动页面以加载可能的懒加载图片
                self.scroll_to_load(driver, max_scrolls=3)

                # 获取所有图片标签
                img_tags = masonry_div.find_elements(By.TAG_NAME, "img")

                if not img_tags:
                    print(f"未找到图片标签 -> {url}")
                    return all_urls

                for img in img_tags:
                    # 尝试获取src属性，如果src为空则尝试data-src（懒加载）
                    pic_url = img.get_attribute("src") or img.get_attribute("data-src") or img.get_attribute("data-original")
                    if pic_url and pic_url.startswith('http'):  # 确保是有效的URL
                        all_urls.append(pic_url)

                print(f"共找到图片: {all_urls}...")

                # 随机延迟
                await asyncio.sleep(random.uniform(2, 4))

                # 下载图片（调用异步函数）
                if all_urls:
                    await download_images(all_urls, r'D:\DATA\pictures\流程图1',max_concurrent=1,proxy=True)
                break

            except Exception as e:
                print(f"爬取异常: {e} -> {url}")
                df = pd.DataFrame([url])
                df.to_csv(r'D:\DATA\pictures\失败的图片.csv', mode='a', header=False,index=False, encoding='utf-8-sig')
                traceback.print_exc()
                retry_count += 1
                await asyncio.sleep(random.uniform(1,3))

            finally:
                if driver:
                    driver.quit()

        return all_urls

    async def crawler(self, urls):
        """并发爬取多个URL"""
        async def crawler_with_semaphore(url):
            async with self.semaphore:
                return await self.crawler_main(url)

        tasks = [crawler_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        all_pic_urls = []
        for result in results:
            if isinstance(result, Exception):
                print(f"任务执行异常: {result}")
            elif result:
                all_pic_urls.extend(result)

        return all_pic_urls

async def main():
    end = 1091
    step = 1
    all_urls = []

    # 生成URL列表
    for i in range(1, end, step):
        url = f'https://www.freedgo.com/new/search/3/0/d_0_3_0_0_{i}_0_0.html'
        all_urls.append(url)

    # 限制测试数量（可以先测试少量）
    test_urls = all_urls[:5]  # 先测试前5个

    print(f"开始爬取 {len(test_urls)} 个URL...")

    # 创建爬虫实例
    crawler = ProxyCrawler(max_concurrent=2)  # 降低并发数

    # 开始爬取
    results = await crawler.crawler(test_urls)

    print(f"爬取完成，共找到 {len(results)} 个图片URL")


if __name__ == '__main__':
    asyncio.run(main())


