import ijson
import os
import hashlib
from utils.file_io import DealFile
import pandas as pd
import shutil
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
                            content = con['title'] + con["content"]
                            res = {
                                "lan": con["language"],
                                "labels": labels,
                                "md5": hashlib.md5(content.encode("utf-8")).hexdigest(),
                                "url": con["url"],
                                "file_type": file_type,
                                "filename": con["id"]
                            }

                            data.append(res)

        df = pd.DataFrame(data)
        df.drop_duplicates(subset=['md5'], keep='first', inplace=True)
        df.to_csv(csv_path, mode="a",encoding="utf-8-sig",header=False,index=False)
        print(f"[INFO] {csv_path}文件保存成功 -> 共{len(df.values.tolist())}条数据")

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

    def to_csv(self, path, csv_path,mode='a'):
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
                        data['type'].append(os.path.basename(path))
            if os.path.exists(csv_path):
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            pd.DataFrame(data).to_csv(csv_path,mode=mode,index=False, header=False, encoding="utf-8-sig")
            print(f'[INFO] 图片数据保存成功')
        except Exception as e:
            print(f'[False] 图片数据保存失败:{e}')

import re
class MurderToCSV(DealFile):
    """csv文件去重"""
    def __init__(self,path):
        super().__init__()
        self.path = path

    def normalize_filename(self):
        """初始化文件名"""
        second_name = os.listdir(self.path)
        for file in second_name:
            folder_name = os.path.join(self.path,file)
            if not os.path.isdir(folder_name):
                continue
            third_name = os.listdir(folder_name)
            for name in third_name:
                # 只保留汉字
                match = re.search(r'[\u4e00-\u9fff]', name)
                if match:
                    # 返回从第一个汉字开始的子字符串
                    new_name = name[match.start():]
                else:
                    new_name = name
                patternr = "（.*"
                new_name = re.sub(patternr, r"", new_name)
                old_path = os.path.join(folder_name,name)
                new_path = os.path.join(folder_name,new_name)
                if os.path.exists(new_path):
                    continue
                os.rename(old_path,new_path)

    def tocsv(self):
        second_files = os.listdir(self.path)
        count = 0
        data = []
        seen = set()
        dup_data = []
        output_path = os.path.join(self.path,"seen.csv")
        dup_path = os.path.join(self.path,'dup_seen.csv')
        for file in second_files:
            second_path = os.path.join(self.path,file)
            if not os.path.isdir(second_path):
                continue

            third_filename = os.listdir(second_path)
            for filename in third_filename:
                res = {
                    '剧本类型':file,
                    '剧本名': filename
                }
                if res['剧本名'] not in seen:
                    seen.add(res['剧本名'])
                    data.append(res)
                else:
                    dup_data.append(res)
                    path = os.path.join(self.path,file,filename)
                    move_path = os.path.join(self.path,"dup")
                    os.makedirs(move_path, exist_ok=True)
                    if not os.path.exists(path):
                        shutil.move(path,move_path)
                    else:
                        shutil.rmtree(path)

                if len(data) % 100 == 0:
                    df = pd.DataFrame(data)
                    df.to_csv(output_path, index=False, header=False, encoding="utf-8-sig",mode='a')
                    data = []
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, header=False, encoding="utf-8-sig", mode='a')
        if dup_data:
            dup_df = pd.DataFrame(dup_data)
            dup_df.to_csv(dup_path, index=False, header=False, encoding="utf-8-sig")
        print('[INFO] CSV文件保存成功')




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
                else:
                    count += 1
        print(count)

    def duplicate_data(self,path):
        """按照 URL 去重，只保留第一次出现的数据"""
        df = pd.read_csv(path, encoding="utf-8-sig", header=None)
        print(df.columns)
        df_unique = df.drop_duplicates(subset=[3], keep='first')
        print(df_unique)
        df_unique.to_csv(path, encoding="utf-8-sig", index=False, header=False)

