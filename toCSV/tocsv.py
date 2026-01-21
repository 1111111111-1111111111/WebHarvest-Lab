"""
文本数据转CSV
"""
# from utils.file_io import DealFile
# import os
# import uuid
# dealfile = DealFile()
# path = r"D:\DATA\多语言语料文本采集\越南语\总-畜牧业"
# output_path = r"D:\DATA\DATA\东盟十国特定领域文本采集\越南语\畜牧业"
# url_to_content = {}
# for file in os.listdir(path):
#     if file.endswith(".json"):
#         content = dealfile.read_json(file, path)
#         url_to_content[content["url"]] = content
# filename = str(uuid.uuid4())
# dealfile.write_json_list(filename, output_path, list(url_to_content.values()))
# print(f'保存成为json文件成功')


"""
图片数据转CSV
"""
from utils.to_csv import PictureToCSV
pc = PictureToCSV()
picture_folder = r'D:\DATA\DATA\Pictures'
csv_path = r'D:\DATA\DATA\Pictures\seen.csv'
pc.to_csv(picture_folder,csv_path)

"""
CSV通用
"""
# from utils.to_csv import ConfigCSV
# cc = ConfigCSV()
## 获取数据长度 - json pdf jpg png
# cc.len_data(r"D:\DATA\DATA")
## csv 文件去重
# cc.duplicate(r"d://seen.csv")