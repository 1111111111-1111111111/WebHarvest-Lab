import ijson
import os
import hashlib
from utils.file_io import DealFile
import pandas as pd
dealfile = DealFile()


class TEXTToCSV(DealFile):
    def __init__(self):
        super().__init__()
        self.dic = {"越南语":"vi","印尼语":"id","马来语":"ms","泰语":"th",
                    "缅甸语":"my","高棉语":"km","老挝语":"lo","菲律宾语":"tl" }

    def to_csv(self,path):
        """转换成csv文件查看是否由空缺值"""
        csv_path = os.path.join(path, "seen.csv")
        exist_con = []
        exist_urls = []
        if os.path.exists(csv_path):
            exist_con = pd.read_csv(csv_path,header=None)
            exist_urls = exist_con.iloc[:,3].tolist()
        columns = ['lan', 'labels','md5', 'url',  'file_type', "filename"]
        data = []
        for root, dirs, files in os.walk(path):
            for file in files:
                str_ = str(root).split("\\")[-1]
                labels = str_
                if file.endswith(".json"):
                    file_type = "json"
                    json_path = os.path.join(root, file)
                    with open(json_path, "rb") as f:
                        parser = ijson.items(f, "item")
                        for con in parser:
                            if con['url'] in exist_urls:
                                continue
                            res = {
                                "lan": con["language"],
                                "labels": labels,
                                "md5": hashlib.md5(con["content"].encode("utf-8")).hexdigest(),
                                "url": con["url"],
                                "file_type": file_type,
                                "filename": con["id"]
                            }

                            data.append(res)

        df = pd.DataFrame(data)
        df.to_csv(csv_path, mode="a",encoding="utf-8-sig",header=False,index=False)

    def json_to_csv(self, url, data, base_path):
        content_md5 = hashlib.md5(data["content"].encode("utf-8")).hexdigest()
        os.makedirs(base_path, exist_ok=True)

        str_1 = str(base_path).split("\\")[-1]
        labels = str_1
        str_ = str(base_path).split("\\")[-2]
        lan = str_

        res = [{
            "lan": self.dic.get(lan),
            "labels": labels,
            "md5": content_md5,
            "url": url,
            "file_type": "json",
            "filename": data["id"],
        }]

        columns = ['lan', 'labels', 'md5', 'url', 'file_type', "filename"]
        csv_path = os.path.join(base_path,"seen.csv")
        DealFile().write_csv(csv_path, columns, res, "a")

        return True


class PictureToCSV(DealFile):
    """图片数据写入CSV文件中"""

    def __init__(self):
        super().__init__()

    def to_csv(self, path, csv_path):
        base_path = os.path.basename(path)
        seen = set()
        data = {
            'md5': [],
            'extension': [],
            "type":[]
        }
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file:
                        md5, extension = file.split(".")
                        if md5 not in seen:
                            seen.add(md5)
                        else:
                            continue
                        data['md5'].append(md5)
                        data['extension'].append(extension)
                        data['type'].append("流程图")
            if os.path.exists(csv_path):
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            pd.DataFrame(data).to_csv(csv_path,index=False, header=False, encoding="utf-8-sig")
            print(f'图片数据保存成功')
        except Exception as e:
            print(f'图片数据保存失败:{e}')

class ConfigCSV:
    def __init__(self):
        pass

    def len_data(self,path):
        """统计内容长度"""
        all_urls = set()
        count = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    with open(json_path, "rb") as f:
                        parser = ijson.items(f, "item")
                        for con in parser:
                            if con["url"] in all_urls:
                                continue
                            all_urls.add(con["url"])
                            count += 1
                elif file.endswith(".pdf"):
                    count += 1
                elif file.endswith(".jpg"):
                    count += 1
                elif file.endswith(".png"):
                    count += 1
        print(count)

    def duplicate_data(self,path):
        """按照 URL 去重，只保留第一次出现的数据"""
        df = pd.read_csv(path, encoding="utf-8-sig", header=None)
        print(df.columns)
        df_unique = df.drop_duplicates(subset=[3], keep='first')
        print(df_unique)
        df_unique.to_csv(path, encoding="utf-8-sig", index=False, header=False)

