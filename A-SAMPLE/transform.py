import json
import os
from openai import OpenAI


def transform_text(text):
    client = OpenAI(
        api_key="sk-2eaf569080d64bacaf3dd60572454941",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    def translate_to_chinese(text, source_lang="auto"):
        """将文本翻译成中文"""
        try:
            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个专业的翻译助手，负责将各种语言准确翻译成中文"},
                    {"role": "user", "content": f"请将以下文本翻译成中文：\n\n{text}"}
                ],
                temperature=0.3  # 降低随机性，提高翻译准确性
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"翻译失败: {e}")
            return None

    # 使用示例
    original_text = text
    translated = translate_to_chinese(original_text)
    return translated


def deal_jsonl(path):
    for filename in os.listdir(path):
        if filename.endswith(".jsonl"):
            file_path = os.path.join(path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = json.load(file)
                text = str(content['input']).replace('\n', ' ').replace('\t',' ')
                output_content = transform_text(text)
                if not output_content:
                    print(f'{filename}')
                    continue

            res = {
                'id': content['id'],
                'input': text,
                'output':output_content.replace('\n', ' '),
                'ori': content['ori'],
                'source_language':content['source_language'],
                 "target_language": "Chinese",
                'info': {
                    'domain': content['info']['domain'],
                    'URL': content['info']['URL']
                }
            }
            print(res)
            output_path = os.path.join(r"D:\样例\李馨彤-金融\平行语料",filename)
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(res, file, ensure_ascii=False, indent=4)

def main():
    path = r"D:\样例\李馨彤-金融\单语料语种1"
    deal_jsonl(path)


if __name__ == '__main__':
    main()
