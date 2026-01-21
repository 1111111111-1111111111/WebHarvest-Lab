import os
import re
import json
def main():
    for file in os.listdir(r'D:\样例\波兰语-pl\单语'):
        if file.endswith('.jsonl'):
            file_path = os.path.join(r'D:\样例\波兰语-pl\单语', file)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = data['input']
                text = re.sub(r'[^\w\s]', '', text)
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()


    main()