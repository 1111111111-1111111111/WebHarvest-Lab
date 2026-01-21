import json
import os
import uuid
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pandas as pd
# 配置 Selenium 选项
def setup_driver():
    chrome_options = Options()

    # 基础配置
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 添加常用请求头
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    # 无头模式（生产环境建议启用）
    # chrome_options.add_argument('--headless=new')
    # 禁用GPU加速（某些环境下可能需要）
    # chrome_options.add_argument('--disable-gpu')
    # 禁用沙盒模式
    # chrome_options.add_argument('--no-sandbox')
    # 禁用开发者模式扩展
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 初始化驱动
    try:
        service = Service(executable_path='D:/python_pro/chromedriver/chromedriver.exe')  # 修改为你的 ChromeDriver 路径
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"手动指定路径也失败: {e}")
        raise

    # 执行 JavaScript 隐藏 WebDriver 特征
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })

    return driver


def crawler(url):
    driver = None
    try:
        # 初始化浏览器
        driver = setup_driver()

        # 访问目标 URL
        print(f"正在访问: {url}")
        driver.get(url)

        # 等待页面加载，处理 Cloudflare 挑战
        wait_time = 10  # 初始等待时间

        # 检查是否有 Cloudflare 挑战
        if "Just a moment" in driver.title or "Cloudflare" in driver.page_source:
            print("检测到 Cloudflare 保护，等待挑战完成...")
            # 增加等待时间
            wait_time = 30

        # 等待页面完全加载
        try:
            # 等待直到找到特定元素或超时
            WebDriverWait(driver, wait_time).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            # 额外等待，确保动态内容加载
            time.sleep(3)

            # 检查是否仍在挑战页面
            if "Just a moment" in driver.title or "Enable JavaScript and cookies" in driver.page_source:
                print("仍然在 Cloudflare 挑战页面，尝试滚动页面触发验证...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(5)

        except Exception as e:
            print(f"页面等待异常: {e}")

        # ============ 等待用户手动操作 ============
        print("\n" + "=" * 60)
        print("👤 需要用户手动操作")
        print("=" * 60)
        print("请手动完成以下操作：")
        print("1. 如果需要，完成 Cloudflare 人机验证")
        print("2. 点击页面上的任何必要按钮（如'继续'、'接受'等）")
        print("3. 等待目标内容完全加载")
        print("4. 滚动页面确保所有内容都已加载")
        print("\n完成后请回到控制台按回车键继续...")
        print("=" * 60)

        # 显示当前页面信息，帮助用户判断
        print(f"\n当前页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")

        # 显示页面是否有目标元素的提示
        try:
            # 检查页面是否已有目标内容
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            div_tag = soup.find('div', {'class': 'T2G6W JYDbo'})

            if div_tag:
                print("✅ 检测到目标元素 'T2G6W JYDbo' 已存在")
                preview = div_tag.get_text(strip=True)[:200] + "..." if div_tag.get_text(strip=True) else "空内容"
                print(f"内容预览: {preview}")
            else:
                print("❌ 未检测到目标元素 'T2G6W JYDbo'")

                # 检查备用元素
                div = soup.find('ul', {'data-start': '67'})
                if div:
                    print("✅ 检测到备用元素 'ul[data-start=\"67\"]' 已存在")
                else:
                    print("❌ 也未检测到备用元素")

                print("请手动操作确保内容加载后按回车继续")
        except:
            print("无法检查页面元素状态")

        # 提供一些操作建议
        print("\n💡 操作建议：")
        print("• 如果看到验证码，请手动完成")
        print("• 如果看到'我不是机器人'复选框，请勾选")
        print("• 如果看到'继续访问'或类似按钮，请点击")
        print("• 可以尝试按 F5 刷新页面")
        print("• 滚动页面查看内容是否加载")

        # 等待用户输入
        input("\n🎯 按回车键继续提取数据...")

        # 可选：在继续前再次检查页面状态
        print("正在重新检查页面状态...")
        try:
            # 等待页面可能的变化
            time.sleep(2)

            # 检查页面标题是否有变化
            new_title = driver.title
            if new_title != driver.title:
                print(f"页面标题已变化: {new_title}")

            # 显示当前URL
            print(f"当前URL: {driver.current_url}")
        except:
            pass

        print("开始提取数据...")
        # ============ 结束用户手动操作 ============

        # 获取页面源码
        html = driver.page_source

        # 使用 BeautifulSoup 解析（保持原逻辑）
        soup = BeautifulSoup(html, 'html.parser')
        div_tag = soup.find('div', {'class': 'T2G6W JYDbo'})

        content = ""
        if not div_tag:
            div_tag = soup.find('ul', {'data-start': '67'})
            if not div_tag:
                print("❌ 错误：未找到目标元素 'T2G6W JYDbo' 或备用元素")
                print("页面标题:", driver.title)
                print("当前URL:", driver.current_url)

                # 可选：保存页面源码用于调试
                debug_path = r'D:\样例\李馨彤-金融\调试页面'
                os.makedirs(debug_path, exist_ok=True)
                debug_file = os.path.join(debug_path, f"debug_{uuid.uuid4().hex[:8]}.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"已保存页面源码到: {debug_file}")

                # 可选：保存截图
                screenshot_file = os.path.join(debug_path, f"screenshot_{uuid.uuid4().hex[:8]}.png")
                driver.save_screenshot(screenshot_file)
                print(f"已保存截图到: {screenshot_file}")

                return None

        p_tag = div_tag.find_all('p')
        for tag in p_tag:
            content += tag.get_text(strip=True)

        if not content:
            print(f'{url} 没有内容')
            return None

        # 显示提取的内容长度
        print(f"✅ 成功提取内容，字符数: {len(content)}")
        print(f"内容预览（前300字符）: {content[:300]}...")

        # 生成唯一 ID 并保存结果（保持原逻辑）
        ID = str(uuid.uuid4())
        res = {
            'id': ID,
            'input': content,
            'ori': urlparse(url).netloc,
            'source_language': 'English',
            'info': {
                'domain': 'news',
                'URL': url
            }
        }

        path = r'D:\样例\李馨彤-金融\单语种语料'
        filepath = os.path.join(path, f'{ID}.jsonl')

        # 确保目录存在
        os.makedirs(path, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)

        print(f'✅ 保存成功: {filepath}')

        return res

    except Exception as e:
        print(f'❌ 爬取失败：{e}')
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        return None

    finally:
        # 确保浏览器被关闭
        if driver:
            print("正在关闭浏览器...")
            driver.quit()
            print("浏览器已关闭")

def main():
    txt_path = r"D:\Scrapy\A-SAMPLE\urls.txt"
    df = pd.read_csv(txt_path, header=None)
    urls = df.iloc[44:,0].tolist()
    for url in urls:
        print(f"\n开始爬取: {url}")
        result = crawler(url)
        if result:
            print(f"成功爬取: {result['id']}")
        else:
            print(f"爬取失败: {url}")

        # 在请求之间添加延迟，避免被封锁
        time.sleep(5)


if __name__ == '__main__':
    main()