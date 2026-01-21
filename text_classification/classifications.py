from tools.classificate_domain import AgricultureClassifier
import os
import json
import shutil
from datetime import datetime
path = r'D:\DATA\多语言语料文本采集\越南语\农业文化1'
agri = AgricultureClassifier()
files = [os.path.join(path, f) for f in os.listdir(path)]
def iterate_json_files(path):
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            filepath = os.path.join(path,filename)
            yield filepath

for file in iterate_json_files(path):
    if not os.path.exists(file):  # 检查文件是否存在
        continue
    if file.endswith('.json'):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result = agri.classify(data['title'],data['content'])

        if result.domain_name != '其它':
            target_path = os.path.join(os.path.dirname(path), result.domain_name)
        else:
            target_path = os.path.join(os.path.dirname(path), '其他')
        try:
            os.makedirs(target_path,exist_ok=True)
            shutil.move(file, target_path)
            print(f'[INFO]{datetime.now()} {file} -> {target_path}')
        except Exception as e:
            print(f'[ERROR] {e}')
