import json
import os
import re, time
from faulthandler import dump_traceback_later

import uuid
from uuid import UUID
import csv
import pandas as pd

__all__ = ["DealFile"]

url_list = []
duplicate_file = []


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class DealFile:
    def __init__(self) -> None:
        pass

    def write_txt(self, filename, base_path, data, mode):
        # 验证基础路径
        directory = os.path.dirname(base_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"【INFO】 创建目录: {directory}")
        # 创建完整路径
        filepath = os.path.join(base_path, f"{filename}")

        # 写入文件
        try:
            with open(filepath, mode, encoding="utf-8") as f:
                f.write(data)
            print(f"【INFO】文件成功写入: {filepath}")
            return True
        except Exception as e:
            print(f"【ERROR】 写入文件失败: {e}")
            return False

    def read_txt(self, filename, base_path):
        filepath = os.path.join(base_path, filename)
        content = ""
        """读取文本文件内容"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"【ERROR】 读取文件失败：{e}")
            return

    def write_json(self, filename, base_path, data):
        filepath = os.path.join(base_path, f"{filename}")
        data_updata = {}
        # 如果文件已存在，先读取现有数据 , 更新数据
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_updata = json.load(f)
            except:
                data_updata = {}
        # 合并数据（避免重复）
        if data_updata:
            print(f"【INFO】 {filepath}存在数据，正在合并数据...")
            data_updata.update(data)
        else:
            # 如果不存在，则只存储原数据
            data_updata = data

        if not os.path.exists(base_path):
            os.makedirs(base_path)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_updata, f, ensure_ascii=False, indent=2, cls=UUIDEncoder)
            # f.write(",\n")
        print(f"【INFO】 {filepath} 文件成功写入！")

    def write_json_list(self, filename, base_path, data):
        filepath = os.path.join(base_path, filename)
        data_updata = []
        # 如果文件已存在，先读取现有数据 , 更新数据
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_updata = json.load(f)
            except:
                data_updata = []
        # 合并数据（避免重复）
        if data_updata:
            print(f"【INFO】 {filepath}存在数据，正在合并数据...")
            data_updata.extend(data)
        else:
            # 如果不存在，则只存储原数据
            data_updata = data

        if not os.path.exists(base_path):
            os.makedirs(base_path,exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_updata, f, ensure_ascii=False, indent=2, cls=UUIDEncoder)
        print(f"【INFO】 {filepath} 文件成功写入！")

    def read_json(self, filename, file_path):
        """读取文件链接"""
        file_path = os.path.join(file_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                dic = json.load(f)
                if not dic:
                    print(f"【ERROR】 {file_path}不存在内容")
                    return None

            print(f"【INFO】 成功读取json文件{file_path}")
            return dic
        except FileNotFoundError:
            print(f"【ERROR】 文件未找到: {file_path}")
        except json.JSONDecodeError:
            print(f"【ERROR】 JSON格式错误: {file_path}")
            return None
        except Exception as e:
            print(f"【ERROR】 读取文件失败: {file_path}, 错误: {e}")
            return None

    def folder_write(self, base_path, dic):
        """
        批量写入文件
        """

        for key, value in dic.items():
            filepath = os.path.join(base_path, key)
            self.write_json(filepath, value)
            print(f"【INFO】 {key} 文件成功写入！")

    def len_JSON(self, filename,filepath):
        """
        求 JSON 格式共有多少条数据
        """
        data_list = self.read_json(filename,filepath)
        print(f"【INFO】 共包含{len(data_list)}条数据")

    def clean_filename(self, filename):
        """
        清洗文件名
        """
        # Windows禁止的字符
        forbidden = '<>:"/\\|?*'
        for char in forbidden:
            filename = filename.replace(char, " ")

        filename = re.sub(r'\s+', '', filename)
        return filename

    def folder_read(self, folder_path):
        if not folder_path:
            raise ValueError("【ERROR】 文件夹路径不能为空")

        # 标准化路径
        folder_path = os.path.normpath(folder_path)

        dirname = os.path.dirname(folder_path)
        if not os.path.exists(dirname):
            print(f"【ERROR】 {dirname}文件夹不存在")
            return None

        content_dic = {}
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith(".txt") or filename.endswith(".json"):
                    try:
                        if filename.endswith(".txt"):
                            content = self.read_txt(filename, root)
                        else:  # .json 文件
                            content = self.read_json(filename,root)
                        name = filename.split(".")[0]
                        content_dic[name] = content
                        print(f"【INFO】 成功读取文件{filename}")
                    except Exception as e:
                        print(f"【ERROR】 读取文件失败: {filename}, 错误: {e}")
                        continue
        return content_dic

    def read_json_folder(self, base_path):
        result_dict = []
        # 遍历目录树
        for root, _, files in os.walk(base_path):
            for filename in files:
                file_path = os.path.join(root, filename)

                # 获取相对路径
                relative_path = os.path.relpath(file_path, base_path)

                try:
                    # 读取并解析JSON文件
                    file_content = self.read_json(file_path)

                    # 添加相对路径到字典
                    file_content["relative_path"] = relative_path.replace('\\', '/')

                    result_dict.append(file_content)

                except json.JSONDecodeError as e:
                    print(f"【ERROR】 JSON解析错误: {file_path}")
                except Exception as e:
                    print(f"【ERROR】 读取文件出错 {file_path}: {str(e)}")
        print(f"【INFO】 所有文件读取完毕")
        return result_dict

    def write_csv_(self, base_path, columns, data, mode,filename):
        file_path = os.path.join(base_path, "seen.csv")

        # 确保父目录存在
        os.makedirs(base_path, exist_ok=True)

        # 确保所有数据都包含这些字段
        processed_data = []
        for item in data:
            # 创建一个包含所有字段的新字典
            processed_item = {}
            for filename in columns:
                if filename =="content":

                    processed_item[filename] = item.get(filename, '')
                processed_item[filename] = item.get(filename, '')  # 如果字段不存在，使用空字符串

            processed_data.append(processed_item)

        with open(file_path, mode, newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            # writer.writeheader()
            writer.writerows(processed_data)

        print(f"【INFO】 文件写入成功")
    def write_csv(self, base_path, columns, data,mode):
        file_path = os.path.join(base_path, "seen.csv")

        # 确保父目录存在
        os.makedirs(base_path, exist_ok=True)

        # 确保所有数据都包含这些字段
        processed_data = []
        for item in data:
            # 创建一个包含所有字段的新字典
            processed_item = {}
            for fieldname in columns:
                processed_item[fieldname] = item.get(fieldname, '')  # 如果字段不存在，使用空字符串

            processed_data.append(processed_item)

        with open(file_path, mode, newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            # writer.writeheader()
            writer.writerows(processed_data)

        print(f"【INFO】 文件写入成功")

    def read_csv(self, filepath):
        df = pd.read_csv(filepath, encoding="utf8")

        # 提取列数据并转换为列表
        url_column = df["url"].tolist()
        id_column = df["id"].tolist()

        urls = []
        for url, id in zip(url_column, id_column):
            urls.append({
                "url": url,
                "id": id
            })
        return urls

    def files_count(self, path):
        files = os.listdir(path)
        print(len(files))
        return len(files)

    def concate_file(self):
        pass


# 使用示例
if __name__ == "__main__":
    dealfile = DealFile()

    # content_dic = dealfile.read_json(r"D:\Scrapy\DATA\多语言语料文本采集\高棉语\新闻\d5688229-ec14-4778-9721-a6dafc52846c.json")