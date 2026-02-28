import re
from typing import Dict, List, Tuple, Any
from config.asean10Countries_keyword_library import ClassificationResult, KeywordSet, Domain, DOMAIN_NAMES, \
    build_keyword_library


class AgricultureClassifier:
    def __init__(self):
        # 权重配置
        self.weights = {
            'core': 3.0,
            'extension': 1.5,
            'context': 2.0,
            'exclusion': -5.0,
            'required': 10.0
        }

        # 置信度阈值
        self.confidence_threshold = 0.3

        # 构建关键词库
        self.keyword_library = build_keyword_library()

        # 误匹配过滤词典
        self.false_positives = self._build_false_positives()

        # 领域必需词验证模式
        self.required_validation = self._build_required_validation()

    @staticmethod
    def _build_false_positives() -> Dict[Domain, List[str]]:
        """构建误匹配过滤词典（简化版）"""
        return {
            Domain.FISHERY: [
                r'cá nhân\b',  # 个人
                r'cá thể\b',  # 个体
                r'\bcách\b',  # 方法
                r'\bhồ sơ\b',  # 档案
                r'\bliên hệ với\b',  # 联系
            ],
            Domain.PLANTING: [
                r'cây cầu\b',  # 桥梁
                r'cây số\b',  # 公里
                r'hoa hậu\b',  # 选美皇后
                r'đất nước\b',  # 国家
            ],
            Domain.ANIMAL_HUSBANDRY: [
                r'bò phó\b',  # 副部长
                r'gà tây ban nha\b',  # 西班牙
                r'lợi ích\b',  # 利益
            ],
            Domain.FACILITY_AGRICULTURE: [
                r'nhà trẻ\b',  # 托儿所
                r'nhà hát\b',  # 剧院
            ],
            Domain.TECH_SERVICE: [
                r'dịch vụ công\b',  # 公共服务
            ]
        }

    @staticmethod
    def _build_required_validation() -> Dict[Domain, List[str]]:
        """构建必需词验证模式"""
        return {
            Domain.FISHERY: [
                r'thủy sản\b',
                r'hải sản\b',
                r'ngư nghiệp\b',
                r'cá\s+[\w]+\b',  # cá + 另一个词
                r'tôm\s+[\w]*\b',  # tôm + 后缀
                r'đánh bắt\b',
            ],
            Domain.PLANTING: [
                r'trồng\s+[\w]+\b',
                r'cây\s+[\w]+\b',
                r'lúa\b',
                r'ngô\b',
                r'cà phê\b',
            ],
            Domain.ANIMAL_HUSBANDRY: [
                r'chăn nuôi\s+[\w]*\b',
                r'nuôi\s+[\w]+\s+(lợn|bò|gà)\b',
                r'trại chăn nuôi\b',
            ],
            Domain.FACILITY_AGRICULTURE: [
                r'nhà (kính|màng|lưới)\b',
                r'nông nghiệp công nghệ cao\b',
                r'thủy canh\b',
            ]
        }

    def classify(self, title: str, content: str) -> ClassificationResult:
        """分类主函数"""
        # 合并文本
        text = f"{title or ''} {content or ''}".lower()

        # 预处理文本
        normalized_text = self._normalize_text(text)

        # 计算各领域分数
        domain_scores = {}
        domain_matches = {}

        for domain, keywords in self.keyword_library.items():
            # 验证
            if domain == Domain.OTHER:
                continue

            score, matches = self._calculate_domain_score(
                domain, keywords, normalized_text
            )

            if score > 0:  # 只记录有得分的领域
                domain_scores[domain] = score
                domain_matches[domain] = matches

        # 判断结果
        if not domain_scores:
            return self._get_other_result()

        # 找出最高分领域
        sorted_domains = sorted(
            domain_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_domain, top_score = sorted_domains[0]

        # 计算置信度
        confidence = self._calculate_confidence(
            top_score, domain_scores, normalized_text
        )

        # 最终判断：是否为OTHER
        is_other = self._is_really_other(
            top_domain, confidence, domain_matches[top_domain], normalized_text
        )

        if is_other:
            return self._get_other_result()

        # 准备结果
        return ClassificationResult(
            domain_id=top_domain.value,
            domain_name=DOMAIN_NAMES[top_domain],
            confidence=round(confidence, 3),
            keywords_found=domain_matches[top_domain]["all_matched"],
            evidence={
                "core_matches": domain_matches[top_domain]["core_words"],
                "extension_matches": domain_matches[top_domain]["extension_words"],
                "required_matches": domain_matches[top_domain]["required_words"],
                "total_words": len(normalized_text.split()),
                "keywords_count": len(domain_matches[top_domain]["all_matched"])
            },
            is_other=False
        )

    def _calculate_domain_score(
            self,
            domain: Domain,
            keywords: KeywordSet,
            text: str
    ) -> Tuple[float, Dict[str, Any]]:
        """精准计算领域分数"""
        score = 0.0
        matches = {
            "required_words": [],
            "core_words": [],
            "extension_words": [],
            "context_words": [],
            "exclusion_hits": [],
            "all_matched": []
        }

        # # 1. 检查排除词（优先检查，如果命中排除词，直接返回负分）
        # for word in keywords.exclusion_words:
        #     if self._exact_match(word, text):
        #         score += self.weights['exclusion']
        #         matches["exclusion_hits"].append(word)

        # # 2. 检查必需词（没有必需词匹配，直接返回0分）
        # has_required = False
        # for word in keywords.required_words:
        #     if self._exact_match(word, text) and not self._is_false_positive(word, text, domain):
        #         # 验证必需词的真实性
        #         if self._validate_required_word(word, text, domain):
        #             score += self.weights['required']
        #             matches["required_words"].append(word)
        #             matches["all_matched"].append(word)
        #             has_required = True
        #             break

        # if not has_required:
        #     return 0.0, matches

        # 3. 检查核心词
        for word in keywords.core_words:
            if self._exact_match(word, text) and not self._is_false_positive(word, text, domain):
                score += self.weights['core']
                matches["core_words"].append(word)
                matches["all_matched"].append(word)

        # 4. 检查扩展词
        for word in keywords.extension_words:
            if self._exact_match(word, text) and not self._is_false_positive(word, text, domain):
                score += self.weights['extension']
                matches["extension_words"].append(word)
                matches["all_matched"].append(word)

        # 5. 检查上下文词
        for word in keywords.context_words:
            if self._exact_match(word, text) and not self._is_false_positive(word, text, domain):
                score += self.weights['context']
                matches["context_words"].append(word)
                matches["all_matched"].append(word)

        # 6. 领域特定分数调整
        score = self._apply_domain_adjustment(score, domain, matches, text)

        return score, matches

    @staticmethod
    def _exact_match(keyword: str, text: str) -> bool:
        """精确单词匹配（带边界）"""
        # 转义特殊字符
        escaped = re.escape(keyword)
        # 使用单词边界（考虑越南语字符）
        pattern = rf'(^|\W){escaped}($|\W)'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def _is_false_positive(self, word: str, text: str, domain: Domain) -> bool:
        """检查是否为误匹配"""
        if domain not in self.false_positives:
            return False

        for pattern in self.false_positives[domain]:
            # 检查这个词是否匹配误匹配模式
            if re.search(pattern, word, re.IGNORECASE):
                return True

        return False

    def _validate_required_word(self, word: str, text: str, domain: Domain) -> bool:
        """验证必需词的真实性"""
        if domain not in self.required_validation:
            return True

        # 对于需要验证的领域，检查是否有真正的领域词汇
        for pattern in self.required_validation[domain]:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def _apply_domain_adjustment(
            score: float,
            domain: Domain,
            matches: Dict[str, List[str]],
            text: str
    ) -> float:
        """应用领域特定的分数调整"""
        if domain == Domain.FISHERY:
            # 渔业：单独出现"cá"无效
            if "cá" in [w.lower() for w in matches["core_words"]]:
                # 检查是否有其他渔业词汇
                other_fishery = any(
                    kw in text for kw in ["thủy sản", "hải sản", "ngư nghiệp", "tôm", "cua"]
                )
                if not other_fishery:
                    return score * 0.3  # 严重惩罚

        elif domain == Domain.PLANTING:
            # 种植业：单独出现"cây"无效
            if "cây" in [w.lower() for w in matches["core_words"]]:
                other_planting = any(
                    kw in text for kw in ["trồng", "lúa", "ngô", "rau", "hoa quả"]
                )
                if not other_planting:
                    return score * 0.5

        elif domain == Domain.ANIMAL_HUSBANDRY:
            # 畜牧业：单独动物名称需要验证
            animal_words = ["lợn", "bò", "gà", "vịt"]
            matched_animals = [w for w in matches["core_words"] if w.lower() in animal_words]

            if matched_animals and "chăn nuôi" not in text:
                # 只有动物名称，没有"chăn nuôi"上下文
                return score * 0.6

        return score

    def _calculate_confidence(
            self,
            top_score: float,
            all_scores: Dict[Domain, float],
            text: str
    ) -> float:
        """计算置信度"""
        if top_score <= 0:
            return 0.0

        # 基础置信度（基于分数）
        max_possible = 50.0
        base_confidence = min(top_score / max_possible, 1.0)

        # 竞争差距因子
        if len(all_scores) > 1:
            sorted_scores = sorted(all_scores.values(), reverse=True)
            gap = sorted_scores[0] - sorted_scores[1]
            gap_factor = min(gap / max(sorted_scores[0], 1), 1.0)
        else:
            gap_factor = 1.0

        # 关键词密度因子
        words = text.split()
        keywords_count = sum(1 for word in words if any(
            self._exact_match(kw, word) for domain in all_scores.keys()
            for kw in self.keyword_library[domain].core_words
        ))

        density = keywords_count / max(len(words), 1)
        density_factor = min(density * 5, 1.0)

        # 综合置信度
        confidence = (
                base_confidence * 0.4 +
                gap_factor * 0.4 +
                density_factor * 0.2
        )

        return min(max(confidence, 0.0), 1.0)

    def _is_really_other(
            self,
            domain: Domain,
            confidence: float,
            matches: Dict[str, List[str]],
            text: str
    ) -> bool:
        """判断是否真的应该归为OTHER"""

        # 1. 置信度过低
        if confidence < self.confidence_threshold:
            return True

        # 2. 没有匹配到核心词
        if not matches["core_words"]:
            return True

        # 3. 检查是否为误匹配
        if domain == Domain.FISHERY:
            # 渔业：只有"cá"一个词
            core_words_lower = [w.lower() for w in matches["core_words"]]
            if len(core_words_lower) == 1 and "cá" in core_words_lower:
                # 检查上下文中是否有真正的渔业内容
                if not any(kw in text for kw in ["thủy sản", "hải sản", "ngư", "tôm", "cua"]):
                    return True

        elif domain == Domain.PLANTING:
            # 种植业：只有"cây"一个词
            core_words_lower = [w.lower() for w in matches["core_words"]]
            if len(core_words_lower) == 1 and "cây" in core_words_lower:
                if not any(kw in text for kw in ["trồng", "lúa", "ngô", "rau"]):
                    return True

        # 4. 匹配的关键词太少
        total_matches = len(matches["all_matched"])
        if total_matches < 2:  # 至少需要2个关键词
            return True

        return False

    @staticmethod
    def _normalize_text(text: str) -> str:
        """标准化文本"""
        # 替换换行和多余空格
        text = re.sub(r'\s+', ' ', text.strip())
        # 添加边界空格
        return f" {text} "

    @staticmethod
    def _get_other_result() -> ClassificationResult:
        """获取OTHER领域结果"""
        return ClassificationResult(
            domain_id=Domain.OTHER.value,
            domain_name="其它",
            confidence=0.0,
            keywords_found=[],
            evidence={
                "reason": "未匹配到农业相关关键词",
                "total_words": 0
            },
            is_other=True
        )


# 测试函数
def test_classifier():
    """测试分类器"""
    classifier = AgricultureClassifier()

    # 测试文本1：企业注册服务（应该分类为OTHER）
    test_text1 = """
Chiến dịch mang tên Sophia của Liên minh châu Âu có mục tiêu ban đầu là ngăn chặn và bắt giữ các nhóm buôn người, đưa người tị nạn từLibya vượt Địa Trung Hải sang châu Âu. Từ năm 2015, các tàu quân sự châu Âu thay nhau tuần tra trên biển đã giúp giảm 80% lượng người tị nạn vượt biển vào châu Âu.Phó Chủ tịch Ủy ban châu Âu Federica Mogherini muốn mở rộng phạm vi hoạt động của chiến dịch này sang kiểm soát việc chuyên chở vũ khí và dầu mỏ của Libya.Libya đang phải chịu cấm vận của Liên Hợp Quốc, không được nhập khẩu vũ khí, không được xuất khẩu dầu mỏ ngoài mức cho phép của Liên Hợp Quốc.Theo bàFederica Mogherini, chiến sự bùng phát tạiLibya từ hai tuần trở lại đây có nguy cơ biến thành cuộc nội chiến dài lâu. Nếu vũ khí được tuồn thêm vàoLibya thì tình hình sẽ tồi tệ thêm.Phó Chủ tịch Ủy ban châu Âutuyên bố rằng, chỉ có cách đưa thêm tàu tuần tra tới Địa Trung hải thì lệnh cấm vận của Liên Hợp Quốc mới thực hiện được và hy vọng các nước sẽ điều thêm tàu quân sự tới đây trong vài tuần tới.Theo vtv.vnCopy linkLink bài gốcLấy linkhttps://vtv.vn/the-gioi/eu-keu-goi-trien-khai-tau-chien-tai-dia-trung-hai-20190417220048407.htmTheo vtv.vn
"""


    tests = [
        ("企业注册服务", test_text1),
    ]

    for name, text in tests:
        print(f"\n=== 测试: {name} ===")
        result = classifier.classify("", text)
        print(f"分类: {result.domain_name} (置信度: {result.confidence})")
        print(f"匹配关键词: {', '.join(result.keywords_found[:5])}")


if __name__ == "__main__":
    test_classifier()
