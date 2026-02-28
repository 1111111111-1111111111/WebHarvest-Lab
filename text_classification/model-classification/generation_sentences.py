import json
import random
from typing import List, Dict
from config.asean10Countries_keyword_library import build_keyword_library,KeywordSet,Domain,DOMAIN_NAMES

class TrainingDataGenerator:
    def __init__(self, domain_keywords):
        self.domain_keywords = domain_keywords
        
    def generate_text_for_domain(self, domain: Domain, num_samples: int = 50) -> List[str]:
        """为特定领域生成训练文本"""
        keyword_set = self.domain_keywords[domain]
        texts = []
        
        for _ in range(num_samples):
            # 随机选择核心词和扩展词
            num_core = random.randint(3, 6)
            num_extension = random.randint(2, 4)
            num_context = random.randint(1, 3)
            
            selected_core = random.sample(keyword_set.core_words, num_core)
            selected_extension = random.sample(keyword_set.extension_words, num_extension)
            selected_context = random.sample(keyword_set.context_words, num_context)
            
            # 生成句子结构
            sentences = []

            # 核心句子
            core_sentence = self._make_sentence(selected_core)
            sentences.append(core_sentence)
            
            # 扩展句子
            if selected_extension:
                ext_sentence = f"Kỹ thuật {random.choice(['hiện đại', 'tiên tiến', 'mới'])} bao gồm: " + \
                             ", ".join(selected_extension[:3]) + "."
                sentences.append(ext_sentence)
            
            # 上下文句子
            if selected_context:
                ctx_sentence = f"Trong {domain.name.lower()}, {random.choice(selected_context)} là rất quan trọng."
                sentences.append(ctx_sentence)
            
            # 组合成完整文本
            text = " ".join(sentences)
            
            # 添加一些随机段落
            if random.random() > 0.5:
                text += " " + self._add_random_paragraph(keyword_set)
            
            texts.append(text)
        
        return texts
    
    def _make_sentence(self, words: List[str]) -> str:
        """创建自然句子"""
        sentence_patterns = [
            f"tập trung vào các hoạt Sđộng như {', '.join(words[:-1])} và {words[-1]}.",
            f"Trong, {random.choice(words)} là một yếu tố then chốt.",
            f"Các phương pháp bao gồm {', '.join(words[:3])} và nhiều kỹ thuật khác.",
            f"đóng vai trò quan trọng trong việc phát triển {random.choice(words)}.",
        ]
        return random.choice(sentence_patterns)
    
    def _add_random_paragraph(self, keyword_set: KeywordSet) -> str:
        """添加随机段落增加多样性"""
        topics = [
            "Ứng dụng công nghệ",
            "Phát triển bền vững",
            "Quản lý hiệu quả",
            "Nâng cao năng suất",
            "Bảo vệ môi trường"
        ]
        
        topic = random.choice(topics)
        words = random.sample(keyword_set.core_words, 3)
        
        paragraphs = [
            f"{topic} trong lĩnh vực này giúp cải thiện {', '.join(words)}.",
            f"Với {topic}, các nhà sản xuất có thể tối ưu hóa {words[0]} và {words[1]}.",
            f"{topic} là xu hướng hiện nay, đặc biệt trong việc phát triển {words[2]}.",
        ]
        
        return random.choice(paragraphs)
    
    def generate_all_training_data(self, samples_per_domain: int = 50) -> Dict:
        """生成所有领域的训练数据"""
        training_data = {}
        
        for domain in DOMAIN_NAMES:
            if DOMAIN_NAMES[domain] == "其它":
                continue
            # print(f"正在生成 {DOMAIN_NAMES[domain]} 的训练数据...")
            texts = self.generate_text_for_domain(domain, samples_per_domain)
            name_ = str(domain)
            training_data[name_] = texts
        
        return training_data

# 使用示例
if __name__ == "__main__":
    
    generator = TrainingDataGenerator(build_keyword_library())
    training_data = generator.generate_all_training_data(samples_per_domain=500)
    
    # 保存训练数据
    with open('./data/agriculture_data.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    print(f"已生成 {sum(len(v) for v in training_data.values())} 条训练数据")