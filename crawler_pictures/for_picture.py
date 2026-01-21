import json
import pandas as pd
import random,time
import cloudscraper
import ssl
import requests

# 创建忽略SSL验证的session
session = requests.Session()
session.verify = False

# 禁用SSL警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# # 创建scraper时指定更详细的参数
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False,
    },
    interpreter='nodejs',  # 使用Node.js作为JavaScript解释器
    delay=5  # 添加延迟
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://blog.csdn.net/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 先访问主页获取cookie
home_response = scraper.get("https://blog.csdn.net/weixin_61498557", headers=headers,timeout=10)

urls = set()
tmp_urls = set()
cnt = 0 # 记录没有新增链接次数
csv_path = r"flow.csv"
# 再访问API
for i in range(54, 238):
    old_cnt = len(urls)
    time.sleep(random.uniform(1,2))
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = scraper.get(
                f"https://blog.csdn.net/community/home-api/v1/get-business-list?page={i}&size=20&businessType=blog&orderby=&noMore=false&year=&month=&username=weixin_61498557",
                headers=headers
            )

            content = json.loads(response.text)
            print("API状态码:", response.status_code)
            for i in content["data"]["list"]:
                url = i["url"]
                if url not in urls:
                    tmp_urls.add(url)
                    urls.add(url)

            new_cnt = len(urls)
            print(f"当前抓取到 {new_cnt} 个链接")

            if len(tmp_urls) % 10 == 0:
                df = pd.DataFrame(tmp_urls)
                df.to_csv(csv_path, mode="a", header=False, index=False)
                tmp_urls = set()


            if old_cnt == new_cnt:
                cnt += 1
                print(f"第{cnt}次读取，没有新的链接了")

            if cnt > 3:
                print(f"超过 3 次没有新增链接，跳过读取")
                break

        except Exception as e:
            time.sleep(2 ** (attempt+1) )
            print(f"响应出错：{e}")

# 保存剩余的URL
df = pd.DataFrame(urls)
df.to_csv(csv_path,mode="a", header=False,index=False)
print(f"共抓取到{len(urls)}链接")

