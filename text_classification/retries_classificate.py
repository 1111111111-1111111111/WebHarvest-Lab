from tools.classificate_domain import AgricultureClassifier
import os
import json
import shutil


def text__classificate(cf, path):
    """文本重新分类"""
    error_count = processed_count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file:
                continue

            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = json.loads(f.read())

                if text['title'] and text['content']:
                    title, content = text['title'],text['content']
                    processed_count += 1
                result = cf.classify(title, content)

            dir = result.domain_name
            dirname = os.path.dirname(root)
            os.makedirs(fr'{dirname}/{dir}', exist_ok=True)
            target_path = fr'{dirname}/{dir}/{file}'

            if dir == '其它':
                error_count += 1
            else:
                processed_count += 1

            shutil.move(filepath, target_path)
            print(f'{filepath} -> {target_path}')

    print(f'处理完成，成功处理：{processed_count},失败：{error_count}')

def main():
    """主程序"""
    path = r'D:\DATA\多语言语料文本采集\越南语'
    cf = AgricultureClassifier()
    text__classificate(cf, path)


if __name__ == '__main__':
    main()
