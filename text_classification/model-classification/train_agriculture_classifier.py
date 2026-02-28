"""
农业领域文本分类器 - 训练脚本
支持越南语十大农业领域分类
"""
from generation_sentences import TrainingDataGenerator  # 自定义内容
import os
import json
import pickle
import numpy as np
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')  # 全局忽略所有警告信息

# 机器学习库
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.preprocessing import LabelEncoder
from scipy import sparse  #

# 深度学习库（可选）
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer

    USE_DEEP_LEARNING = True
except ImportError:
    USE_DEEP_LEARNING = False
    print("深度学习库未安装，将仅使用传统方法")

# 文本处理
import re
import jieba

class VietnameseTextProcessor:
    """越南语文本处理器"""

    def __init__(self, domain_keywords: Dict):
        self.domain_keywords = domain_keywords
        self.stopwords = self.load_stopwords()
        self.setup_custom_dictionary()

    def load_stopwords(self) -> set:
        """加载越南语停用词"""
        vietnamese_stopwords = [
            'của', 'là', 'và', 'các', 'cho', 'trong', 'với', 'được', 'có', 'một', 'những',
            'này', 'khi', 'từ', 'như', 'bởi', 'về', 'sau', 'còn', 'để', 'nên', 'vì', 'hay',
            'hoặc', 'nếu', 'thì', 'mà', 'làm', 'lại', 'ra', 'nào', 'đây', 'đó', 'khi', 'có',
            'mới', 'đã', 'sẽ', 'đang', 'rất', 'cũng', 'chỉ', 'vẫn', 'lớn', 'nhỏ', 'cao', 'thấp',
            'nhiều', 'ít', 'mọi', 'mỗi', 'tất cả', 'bất kỳ', 'cả', 'đều', 'chính', 'thực',
            'nông', 'nông nghiệp', 'nông thôn', 'phát triển', 'quản lý', 'sản xuất'
        ]
        return set(vietnamese_stopwords)

    def setup_custom_dictionary(self):
        """设置自定义词典"""
        # 将所有领域关键词添加到jieba词典
        for domain, keyword_set in self.domain_keywords.items():
            for word in keyword_set.core_words:
                jieba.add_word(word, freq=1000)
            for word in keyword_set.extension_words:
                jieba.add_word(word, freq=500)

    def clean_text(self, text: str) -> str:
        """清洗文本"""
        if not isinstance(text, str):
            return ""

        # 转换为小写
        text = text.lower()

        # 移除特殊字符但保留越南语字符
        text = re.sub(
            r'[^\w\sàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]',
            ' ', text)

        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize_vietnamese(self, text: str) -> List[str]:
        """越南语分词"""
        # 回退到简单空格分词
        tokens = text.split()
        return tokens

    def process(self, text: str) -> str:
        """完整的文本处理流程"""
        # 清洗
        text = self.clean_text(text)

        # 使用越南语分词
        tokens = self.tokenize_vietnamese(text)

        # 移除停用词
        tokens = [token for token in tokens if token not in self.stopwords and len(token) > 1]

        return ' '.join(tokens)


class AgricultureDomainClassifier:
    """农业领域分类器"""

    def __init__(self,
                 model_type: str = 'tfidf_kmeans',
                 use_keyword_features: bool = True,
                 n_clusters: int = 10):

        self.model_type = model_type
        self.use_keyword_features = use_keyword_features
        self.n_clusters = n_clusters

        # 初始化组件
        self.text_processor = None
        self.vectorizer = None
        self.cluster_model = None
        self.pca = None
        self.domain_mapping = None
        self.domain_keywords = None

        # 结果存储
        self.results = {}

    def load_domain_keywords(self, domain_keywords):
        """加载领域关键词"""
        self.domain_keywords = domain_keywords  # {0: <Domain.PLANTING: 1>, 1: <Domain.PLANTING: 1>, 2: <Domain.PLANTING: 1>, 3: <Domain.PLANTING: 1>, 4: <Domain.PLANTING: 1>, 5: <Domain.ANIMAL_HUSBANDRY: 2>, 6: <Domain.PLANTING: 1>, 7: <Domain.PLANTING: 1>, 8: <Domain.FISHERY: 3>, 9: <Domain.PLANTING: 1>}
        self.text_processor = VietnameseTextProcessor(domain_keywords)

    def extract_features(self, texts: List[str]) -> np.ndarray:
        """提取特征"""
        print("开始特征提取...")

        # 文本预处理
        processed_texts = [self.text_processor.process(text) for text in texts]

        # TF-IDF特征
        print("  提取TF-IDF特征...")
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            tfidf_features = self.vectorizer.fit_transform(processed_texts)
        else:
            tfidf_features = self.vectorizer.transform(processed_texts)

        if self.use_keyword_features:
            # 关键词匹配特征
            print("  提取关键词匹配特征...")
            keyword_features = self.extract_keyword_features(processed_texts)

            # 合并特征
            import scipy.sparse as sp
            features = sp.hstack([tfidf_features, keyword_features])
        else:
            features = tfidf_features

        return features

    def extract_keyword_features(self, texts: List[str]) -> sparse.csr_matrix:
        """提取关键词匹配特征"""
        n_samples = len(texts)
        n_domains = len(self.domain_keywords)
        keyword_features = np.zeros((n_samples, n_domains))

        domain_list = list(self.domain_keywords.keys())

        for i, text in enumerate(texts):
            words = set(text.split())
            for j, domain in enumerate(domain_list):
                keyword_set = self.domain_keywords[domain]
                # 计算核心词匹配度
                core_matches = len(words.intersection(set(keyword_set.core_words)))
                # 计算扩展词匹配度
                ext_matches = len(words.intersection(set(keyword_set.extension_words)))

                # 加权得分
                score = core_matches * 2 + ext_matches * 1
                keyword_features[i, j] = score / 100  # 归一化

        # 转换为稀疏矩阵
        return sparse.csr_matrix(keyword_features)

    def train_clustering(self, features, method: str = 'kmeans'):
        """训练聚类模型"""
        print(f"开始训练聚类模型 ({method})...")

        if method == 'kmeans':
            self.cluster_model = KMeans(
                n_clusters=self.n_clusters,
                random_state=42,
                n_init=10,
                max_iter=300
            )
        elif method == 'hierarchical':
            self.cluster_model = AgglomerativeClustering(
                n_clusters=self.n_clusters,
                linkage='ward'  # 欧式距离
            )
        else:
            raise ValueError(f"不支持的聚类方法: {method}")

        # 训练模型
        if method == 'kmeans':
            self.cluster_model.fit(features)
            labels = self.cluster_model.labels_
        else:
            labels = self.cluster_model.fit_predict(features.toarray())
        return labels

    def assign_domain_names(self, texts: List[str], labels: np.ndarray) -> Dict[int, str]:
        """为聚类分配领域名称"""
        # 统计每个簇的关键词频率
        from collections import Counter
        import numpy as np

        domain_scores = {i: {domain: 0 for domain in self.domain_keywords.keys()}
                         for i in range(self.n_clusters)}

        for idx, (text, label) in enumerate(zip(texts, labels)):
            words = set(self.text_processor.process(text).split())

            for domain, keyword_set in self.domain_keywords.items():
                # 计算匹配分数
                core_match = len(words.intersection(set(keyword_set.core_words)))
                ext_match = len(words.intersection(set(keyword_set.extension_words)))
                score = core_match * 3 + ext_match * 1

                domain_scores[label][domain] += score

        # 为每个簇选择得分最高的领域
        domain_mapping = {}
        for cluster_id in range(self.n_clusters):
            scores = domain_scores[cluster_id]
            if any(scores.values()):  # 如果有得分
                best_domain = max(scores.items(), key=lambda x: x[1])[0]
                domain_mapping[cluster_id] = str(best_domain)
            else:
                # 如果没有明显匹配，使用默认
                domain_mapping[cluster_id] = str(
                    list(self.domain_keywords.keys())[cluster_id % len(self.domain_keywords)])

        self.domain_mapping = domain_mapping
        return domain_mapping

    def evaluate_clustering(self, features: np.ndarray, labels: np.ndarray):
        """评估聚类效果"""
        print("\n聚类效果评估:")
        print("-" * 50)

        # 转换为密集矩阵用于评估
        if hasattr(features, 'toarray'):
            features_dense = features.toarray()
        else:
            features_dense = features

        # 轮廓系数
        if len(set(labels)) > 1:
            silhouette = silhouette_score(features_dense, labels)
            print(f"轮廓系数: {silhouette:.4f}")

            # 解释
            if silhouette > 0.7:
                print("  解释: 聚类结构强")
            elif silhouette > 0.5:
                print("  解释: 聚类结构合理")
            elif silhouette > 0.25:
                print("  解释: 聚类结构较弱")
            else:
                print("  解释: 没有明显的聚类结构")

        # Calinski-Harabasz指数
        ch_score = calinski_harabasz_score(features_dense, labels)
        print(f"Calinski-Harabasz指数: {ch_score:.2f}")

        # 簇大小分布
        unique, counts = np.unique(labels, return_counts=True)
        print(f"\n簇大小分布:")
        for cluster_id, count in zip(unique, counts):
            domain_name = self.domain_mapping.get(cluster_id, f"簇{cluster_id}")
            print(f"  {domain_name}: {count} 个样本 ({count / len(labels) * 100:.1f}%)")

    def train(self, texts: List[str], labels: List[str] = None):
        """训练分类器"""
        print("=" * 60)
        print("开始训练农业领域分类器")
        print("=" * 60)

        # 特征提取
        features = self.extract_features(texts)

        # 训练聚类
        cluster_labels = self.train_clustering(features, method='kmeans')  # 返回形式类似 [2 2 2 ... 3 3 3]

        # 分配领域名称
        domain_mapping = self.assign_domain_names(texts,
                                                  cluster_labels)  # 返回形式类似：{0: <Domain.PLANTING: 1>, 1: <Domain.ANIMAL_HUSBANDRY: 2>, 2: <Domain.PLANTING: 1>, 3: <Domain.PLANTING: 1>}

        # 评估
        self.evaluate_clustering(features, cluster_labels)

        # 如果有真实标签，计算准确率
        if labels is not None:
            self.evaluate_with_labels(cluster_labels, labels)

        print("\n训练完成!")

        return cluster_labels

    def evaluate_with_labels(self, pred_labels, true_labels: List[str]):
        """使用真实标签评估"""
        from sklearn.metrics import accuracy_score, classification_report

        # 将聚类标签映射到领域名称
        pred_domains = []
        for label in pred_labels:
            domain = self.domain_mapping[label]
            # 将枚举对象转换为字符串
            if hasattr(domain, 'value'):
                domain_str = str(domain.value)
            elif hasattr(domain, 'name'):
                domain_str = str(domain.name)
            else:
                domain_str = str(domain)
            pred_domains.append(domain_str)

        # 编码标签
        # 编码标签 - 确保fit和transform使用相同的标签集合
        le = LabelEncoder()
        # 合并所有标签类型以确保编码器知道所有可能的标签
        all_labels = list(set(true_labels + pred_domains))
        le.fit(all_labels)
        # 转换标签
        true_encoded = le.transform(true_labels)
        pred_encoded = le.transform(pred_domains)

        # 计算准确率
        accuracy = accuracy_score(true_encoded, pred_encoded)
        print(f"\n基于真实标签的准确率: {accuracy:.4f}")

        # 分类报告
        print("\n分类报告:")
        print(classification_report(true_labels, pred_domains))

    def predict(self, texts: List[str]) -> List[Tuple[str, float]]:
        """预测文本领域"""
        if self.cluster_model is None:
            raise ValueError("模型未训练，请先调用train方法")

        # 特征提取
        features = self.extract_features(texts)

        # 预测聚类标签
        if isinstance(self.cluster_model, KMeans):
            cluster_labels = self.cluster_model.predict(features)
        else:
            cluster_labels = self.cluster_model.fit_predict(features.toarray())

        # 转换为领域名称
        results = []
        for label in cluster_labels:
            domain = self.domain_mapping.get(label, "未知")

            # 计算置信度（基于到簇中心的距离）
            if isinstance(self.cluster_model, KMeans):
                distances = self.cluster_model.transform(features)
                # 使用softmax将距离转换为置信度
                # 距离越小，置信度越高
                confidence = 1.0 / (1.0 + distances.min(axis=1))
                conf_value = float(confidence[0])
            else:
                conf_value = 0.8  # 层次聚类无法直接计算置信度

            results.append((domain, conf_value))

        return results

    def predict_single(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """预测单个文本，返回top_k个可能领域"""
        # 使用关键词匹配计算每个领域的得分
        processed = self.text_processor.process(text)
        words = set(processed.split())

        domain_scores = []
        for domain, keyword_set in self.domain_keywords.items():
            # 核心词匹配（权重高）
            core_matches = len(words.intersection(set(keyword_set.core_words)))
            # 扩展词匹配（权重中）
            ext_matches = len(words.intersection(set(keyword_set.extension_words)))
            # 上下文词匹配（权重低）
            ctx_matches = len(words.intersection(set(keyword_set.context_words)))

            # 计算总分
            total_score = core_matches * 3 + ext_matches * 2 + ctx_matches * 1

            # 归一化
            max_possible = len(keyword_set.core_words) * 3
            normalized_score = total_score / max_possible if max_possible > 0 else 0

            domain_scores.append((domain, normalized_score))

        # 按得分排序
        domain_scores.sort(key=lambda x: x[1], reverse=True)

        return domain_scores[:top_k]

    def save_model(self, path: str):
        """保存模型"""
        model_data = {
            'model_type': self.model_type,
            'vectorizer': self.vectorizer,
            'cluster_model': self.cluster_model,
            'domain_mapping': self.domain_mapping,
            'domain_keywords': self.domain_keywords,
            'text_processor': self.text_processor
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"模型已保存到 {path}")

    def load_model(self, path: str):
        """加载模型"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.model_type = model_data['model_type']
        self.vectorizer = model_data['vectorizer']
        self.cluster_model = model_data['cluster_model']
        self.domain_mapping = model_data['domain_mapping']
        self.domain_keywords = model_data['domain_keywords']
        self.text_processor = model_data['text_processor']

        print(f"模型已从 {path} 加载")

    def visualize_clusters(self, texts: List[str], labels: np.ndarray = None,
                           save_path: str = None):
        """可视化聚类结果"""
        try:
            import matplotlib.pyplot as plt
            from sklearn.manifold import TSNE

            plt.rcParams['font.sans-serif'] = 'SimHei'  # 解决中文为方块的问题
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题

            # 提取特征
            features = self.extract_features(texts)

            # 如果没有提供标签，使用聚类标签
            if labels is None:
                if isinstance(self.cluster_model, KMeans):
                    labels = self.cluster_model.predict(features)
                else:
                    labels = self.cluster_model.fit_predict(features.toarray())

            # 使用t-SNE降维
            tsne = TSNE(n_components=2, random_state=42, perplexity=30)
            features_2d = tsne.fit_transform(features.toarray())

            # 创建图形
            plt.figure(figsize=(12, 8))

            # 获取颜色
            unique_labels = np.unique(labels)
            colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

            # 绘制每个簇
            for i, label in enumerate(unique_labels):
                # 获取该簇的点
                cluster_points = features_2d[labels == label]

                # 获取领域名称
                domain_name = self.domain_mapping.get(label, f"Cluster {label}")

                # 绘制散点
                plt.scatter(cluster_points[:, 0], cluster_points[:, 1],
                            c=[colors[i]], label=domain_name, alpha=0.6, s=50)

            plt.title('农业领域文本聚类可视化', fontsize=16)
            plt.xlabel('t-SNE Component 1')
            plt.ylabel('t-SNE Component 2')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"可视化图已保存到 {save_path}")

            plt.show()

        except ImportError as e:
            print(f"可视化需要matplotlib和sklearn: {e}")


class DataLoader:
    """数据加载器"""
    @staticmethod
    def load_from_json(filepath: str) -> Dict[str, List[str]]:
        """从JSON文件加载数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    @staticmethod
    def prepare_training_data(data_dict: Dict[str, List[str]]) -> Tuple[List[str], List[str]]:
        """准备训练数据（文本和标签）"""
        texts = []
        labels = []

        for domain, domain_texts in data_dict.items():
            texts.extend(domain_texts)
            labels.extend([domain] * len(domain_texts))

        return texts, labels


def main():
    """主函数"""
    # 配置参数
    CONFIG = {
        'data_path': './data/agriculture_data.json',  # 训练数据路径
        'model_save_path': './models/agriculture_classifier.pkl',
        'visualization_path': './results/cluster_visualization.png',
        'n_clusters': 10,
        'test_samples': [
            "Kỹ thuật trồng lúa nước cần chú ý đến thời vụ, giống lúa và quản lý nước tưới.",  # 种植业
            "Chăn nuôi heo công nghiệp đòi hỏi chuồng trại đạt tiêu chuẩn và thức ăn cân đối dinh dưỡng.",  # 畜牧业
            "Nuôi tôm thẻ chân trắng cần kiểm soát chặt chẽ chất lượng nước và phòng bệnh đốm trắng.",  # 渔业（水产业）
            "Nhà kính trồng rau ứng dụng hệ thống tưới nhỏ giọt tự động và kiểm soát nhiệt độ thông minh.",  # 设施农业
            "Chế biến cà phê rang xay đòi hỏi công nghệ hiện đại để giữ hương vị đặc trưng.",  # 农产品加工业
            "Xuất khẩu gạo sang thị trường EU cần đáp ứng các tiêu chuẩn về dư lượng thuốc bảo vệ thực vật.",  # 农业服务与贸易
            "Dịch vụ kiểm nghiệm nông sản giúp đảm bảo chất lượng và an toàn thực phẩm.",  # 农业服务与贸易
            "Du lịch trải nghiệm nông thôn thu hút khách tham quan vườn cây ăn trái và thưởng thức ẩm thực địa phương.", # 休闲农业与乡村旅游
            "Lễ hội cầu mùa là nét văn hóa truyền thống độc đáo của cộng đồng nông thôn.",  # 农业文化
            "Đào tạo nghề trồng nấm cho lao động nông thôn giúp tạo việc làm và tăng thu nhập.",  # 农业职业教育
            "VinaTech Agri là một trong những doanh nghiệp tiên phong trong lĩnh vực dịch vụ khoa học công nghệ nông nghiệp \
            tại Việt Nam. Công ty chuyên cung cấp các dịch vụ tư vấn kỹ thuật toàn diện cho các trang trại và hợp tác xã, từ  \
            khâu chọn giống, quy trình canh tác, đến giải pháp quản lý dinh dưỡng và bảo vệ thực vật tổng hợp (IPM).Một trọng tâm"   # 农业科技服务业
        ]
    }
    from config.asean10Countries_keyword_library import build_keyword_library
    domain_keywords = build_keyword_library()

    # 1. 加载数据
    if os.path.exists(CONFIG['data_path']):
        training_data = DataLoader.load_from_json(CONFIG['data_path'])
    else:
        # 生成模拟数据（如果没有真实数据）
        generator = TrainingDataGenerator(domain_keywords)
        training_data = generator.generate_all_training_data(samples_per_domain=500)

    # 2. 准备训练数据
    texts, labels = DataLoader.prepare_training_data(training_data)
    print(f"总训练样本数: {len(texts)} -> 对应标签数：{len(labels)}")

    # 3. 训练分类器
    classifier = AgricultureDomainClassifier(
        model_type='tfidf_kmeans',
        use_keyword_features=True,
        n_clusters=CONFIG['n_clusters']
    )

    # 加载领域关键词
    classifier.load_domain_keywords(domain_keywords)

    # 训练模型
    cluster_labels = classifier.train(texts, labels)

    # 4. 保存模型
    classifier.save_model(CONFIG['model_save_path'])

    # 5. 可视化结果
    print("\n步骤5: 生成可视化...")
    try:
        classifier.visualize_clusters(texts[:500], save_path=CONFIG['visualization_path'])
    except Exception as e:
        print(f"可视化失败: {e}")

    # 6. 测试模型
    print("\n步骤6: 测试模型...")
    print("-" * 60)
    for i, test_text in enumerate(CONFIG['test_samples']):
        print(f"\n测试文本 {i + 1}:")
        print(f"  {test_text}")

        # 使用聚类模型预测
        predictions = classifier.predict([test_text])
        domain, confidence = predictions[0]
        print(f"  预测领域: {domain} (置信度: {confidence:.2f})")

        # 使用关键词匹配预测top 3
        top_domains = classifier.predict_single(test_text, top_k=3)
        print(f"  最可能领域 (top 3):")
        for dom, score in top_domains:
            print(f"    - {dom}: {score:.3f}")

    print("\n" + "=" * 60)
    print("农业领域分类器训练完成！")
    print(f"模型已保存至: {CONFIG['model_save_path']}")


if __name__ == "__main__":
    # 创建必要的目录
    os.makedirs('models', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    # 运行主程序
    main()
