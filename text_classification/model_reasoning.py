'''
import torch
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification
import time

class MultilingualClassifier:
    def __init__(self, model_path="xlm-roberta-base", num_labels=15):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 加载多语言模型
        self.tokenizer = XLMRobertaTokenizer.from_pretrained(model_path)
        self.model = XLMRobertaForSequenceClassification.from_pretrained(
            model_path,
            num_labels=num_labels
        ).to(self.device)

        # 东盟语言映射
        self.language_detection = { "vi": "越南语"}

        # 领域标签（可自定义）
        self.domain_labels = {
            0: "种植业", 1: "畜牧业", 2: "渔业（水产业）",
            3: "设施农业", 4: "农产品加工业", 5: "农产品贸易业",
            6: "农业科技服务业", 7: "休闲农业与乡村旅游业", 8: "农业文化",
            9: "农业职业教育", 10: "其它",
        }

    def detect_language(self, text):
        """简单语言检测"""
        if any(ch in 'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệ' for ch in text):
            return "vi"  # 越南语带声调字母
        else:
            return "unknown"

    def predict(self, text, top_k=3):
        """多语言文本分类"""
        # 语言检测
        lang = self.detect_language(text)
        print(f"检测到语言: {self.language_detection.get(lang, '未知')}")

        # 编码和推理
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # 处理结果
        probs = probabilities.cpu().numpy()[0]
        top_indices = probs.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                "领域": self.domain_labels.get(idx, "未知"),
                "置信度": float(probs[idx]),
                "语言": self.language_detection.get(lang, "未知")
            })

        return results

if __name__ == "__main__":
    start_time = time.time()
    model_path = r"D:\Scrapy\models\xlmr"
    classifier = MultilingualClassifier(model_path)

    # 测试不同东盟语言
    test_cases = [
        # 越南语 - 医疗卫生
        "(GLO)- Thông qua dự án hỗ trợ bò sinh sản, nhiều hộ ở xã Ayun (huyện Chư Sê) có thêm sinh kế. Đây chính là “chìa khóa” giúp bà con thoát nghèo bền vững.Từ nguồn vốn của Chương trình giảm nghèo bền vững và phát triển kinh tế-xã hội vùng đồng bào dân tộc thiểu số và miền núi, xã Ayun đã triển khai dự ánhỗ trợ bò sinh sảncho hàng trăm hộ nghèo và cận nghèo đồng bào dân tộc thiểu số.Theo anh Kpui Đe-Trưởng nhóm chăn nuôi cộng đồng làng Hvăk, việc nuôi nhốt bò tập trung theo nhóm hộ giúp quản lý, chăm sóc đàn vật nuôi được tốt hơn.Ảnh: M.PCụ thể, năm 2023, xã hỗ trợ 43 con bò sinh sản cho các hộ nghèo tại làng Keo với tổng số tiền hơn 781 triệu đồng. Năm 2024, hỗ trợ 44 con bò sinh sản cho 22 hộ nghèo tại các làng: Keo, Vơng Chép, Tung Ke và Amil với tổng kinh phí 784 triệu đồng. Tới đây, xã sẽ tiếp tục hỗ trợ 42 con bò cho 21 hộ nghèo ở các làng: Keo, Vơng Chép, Hvăk với kinh phí 773 triệu đồng.Việc hỗ trợ người dân phát triển sản xuất bằng hình thức nuôi bò sinh sản đã tạo chuyển biến tích cực trong nếp nghĩ, cách làm để vươn lên thoát nghèo. Ông Đinh Hnơi-Bí thư Chi bộ làng Keo-cho biết: Qua 3 đợt, làng Keo có 52 hộ được hỗ trợ 62 con bò sinh sản, đáp ứng nhu cầu của người dân.Cũng theo ông Hnơi, khí hậu của địa phương tương đối khắc nghiệt, đất đai bạc màu, đa phần người dân phụ thuộc vào cây lúa, cây mì nên thu nhập còn bấp bênh.Những năm gần đây, nhờ thụ hưởng các chương trình mục tiêu quốc gia, bà con được hỗ trợ phát triển sản xuất thông qua hình thức chăn nuôi bò sinh sản đã tạo thêm động lực để vươn lên gầy dựng cuộc sống.Anh Đinh Suyn (làng Keo) cho hay: Gia đình anh thuộc diện hộ nghèo. Với gần 2 sào lúa, 3 sào mì, mỗi năm, thu nhập của gia đình chưa đến 30 triệu đồng. Năm 2023, anh được Nhà nước hỗ trợ 1 con bò sinh sản. Sau một thời gian chăm sóc, con bò được hỗ trợ đã đẻ bê con khỏe mạnh. Đây là động lực để gia đình vươn lên thoát nghèo.Ủy ban nhân dân xã Ayun cấp bò giống cho các hộ nghèo năm 2024.Ảnh: ĐVCCCòn anh Đinh Byơi (làng Hvăk) thì chia sẻ: Gia đình anh chỉ có gần 4 sào mì nhưng do đất cằn, bạc màu nên thu nhập không đáng kể. Việc anh được xã chọn là đối tượng được hỗ trợ bò sinh sản đã mở cơ hội thoát nghèo. Đến nay, bò mẹ được hỗ trợ đã đẻ 1 bê con và đang tiếp tục mang thai lứa thứ 2.Cùng với việc vay mượn, tích góp, anh mua thêm bò về nuôi. Đến nay, gia đình anh đã có 8 con bò. Dự tính thời gian tới, anh bán bớt số bò này để có vốn đầu tư chăm sóc cây trồng.Theo anh Kpui Đe-Trưởng nhóm chăn nuôi cộng đồng làng Hvăk: Hiện 41 con bò của 34 hộ dân đã sinh sản được 4 bê con và có gần chục con nữa đang chuẩn bị sinh. Đây chính là động lực để người dân trong làng nỗ lực phát triển chăn nuôi, vươn lên thoát nghèo.Để đảm bảo hiệu quả của mô hình, các hộ được hỗ trợ bò đã thành lập nhóm chăn nuôi cộng đồng, bầu ra trưởng nhóm để quản lý việc trông coi và phân công nhiệm vụ cho các thành viên.Anh Đe cho biết: “Trước đây, bà con hay chăn thả rông nên khi tham gia nhóm chăn nuôi cộng đồng theo hình thức nuôi nhốt tập trung, nhiều người còn bỡ ngỡ.Đến nay, bà con đã quen với mô hình này, bởi cách nuôi này thuận lợi cho việc theo dõi sự tăng trưởng của đàn bò, phòng ngừa dịch bệnh kịp thời. Điều quan trọng hơn là bà con có thể chia sẻ kinh nghiệm để cùng nhau quản lý, chăm sóc đàn bò tốt hơn”.Trao đổi với P.V, ông Phạm Ngọc Tuấn-Phó Chủ tịch UBND xã Ayun-cho biết: Toàn xã có 942 hộ, trong đó có 895 hộ đồng bào dân tộc thiểu số. Hiện xã còn 140 hộ nghèo và 187 hộ cận nghèo. Trước đây, địa phương được Nhà nước quan tâm đầu tư nhưng chưa đủ sức để tạo sự đột phá trong công tác giảm nghèo.Thế nhưng, qua 2 năm triển khai thực hiện các dự án hỗ trợ chăn nuôi bò sinh sản đối với hộ nghèo, hộ cận nghèo đã mang lại những kết quả khả quan.Đến nay, có 65/327 hộ nghèo, cận nghèo của xã được hỗ trợ sinh kế bằng hình thức nuôi bò sinh sản. Đặc biệt, số bò trong đợt hỗ trợ năm 2023 đang trong thời kỳ sinh sản, gần 50% số con bò trong số này đã sinh bê con.“Mô hình hỗ trợ bò sinh sản tạo chuyển biến rõ rệt trong nhận thức và đời sống của người dân. Bà con không chỉ có thêm sinh kế để phát triển kinh tế mà còn chủ động hơn trong chăn nuôi. Nhiều hộ từ chỗ khó khăn nay đã có hướng đi ổn định hơn.Thời gian tới, xã tiếp tục giám sát, quản lý và theo dõi chặt chẽ, đồng thời hướng dẫn kỹ thuật chăn nuôi cho các nhóm chăn nuôi cộng đồng để đàn bò phát triển. Bên cạnh đó, xã cũng sẽ tổ chức các lớp tập huấn kỹ thuật phòng bệnh, phối giống và vệ sinh chuồng trại cho các hộ tham gia dự án”-ông Tuấn thông tin.TweetĐánh giá bài viết"
    ]

    results = classifier.predict(test_cases)

    for r in results:
        print(f"  - {r['领域']}: {r['置信度']:.1%} ({r['语言']})")

    end_time = time.time()
    print(end_time-start_time)

'''

import os
import random
import numpy as np
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer,
)
import evaluate
from sklearn.metrics import classification_report, confusion_matrix

# 配置
MODEL_NAME = "xlm-roberta-base"  # 可替换为其他多语种模型
MAX_LENGTH = 256
BATCH_SIZE = 16
NUM_EPOCHS = 4
LEARNING_RATE = 2e-5
SEED = 42
OUTPUT_DIR = "D:/Scrapy/model/myxlmr"

label_list = [
    "PLANTING","ANIMAL_HUSBANDRY","FISHERY","FACILITY_AGRICULTURE",
    "PROCESSING","TRADE","TECH_SERVICE","RURAL_TOURISM",
    "AGRICULTURE_CULTURE","VOCATIONAL_EDU"
]
label2id = {l:i for i,l in enumerate(label_list)}
id2label = {i:l for l,i in label2id.items()}

def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

set_seed()

# 加载数据：假设 CSV 有列 text,label ，label 为字符串类别名
data_files = {
    "train": "train.csv",
    "validation": "valid.csv",
    "test": "test.csv"
}
raw_datasets = load_dataset("csv", data_files=data_files)

# 将 label 字符串映射为 id（如果已经是整数则可跳过）
def map_label(example):
    lab = example["label"]
    if isinstance(lab, str):
        example["label"] = label2id.get(lab, -1)
    return example

raw_datasets = raw_datasets.map(map_label)

# 过滤掉 label=-1 的不明样本（若有）
raw_datasets = raw_datasets.filter(lambda x: x["label"] != -1)

# tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(label_list),
    id2label=id2label,
    label2id=label2id
)

# 预处理（分词）
def preprocess_function(examples):
    texts = examples["text"]
    return tokenizer(texts, truncation=True, padding=False, max_length=MAX_LENGTH)

tokenized_datasets = raw_datasets.map(preprocess_function, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# metrics
accuracy = evaluate.load("accuracy")
f1_macro = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy.compute(predictions=preds, references=labels)["accuracy"]
    f1m = f1_macro.compute(predictions=preds, references=labels, average="macro")["f1"]
    # 生成 classification report（字符串）
    report = classification_report(labels, preds, target_names=label_list, digits=4)
    cm = confusion_matrix(labels, preds)
    # 将报告放入字典便于查看/保存
    return {
        "accuracy": acc,
        "f1_macro": f1m,
        "clf_report": report,
        # 注意：Trainer 的 metric 字典值一般需要可序列化的数值，report 字符串主要用于日志/保存
    }

# TrainingArguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE*2,
    num_train_epochs=NUM_EPOCHS,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="f1_macro",
    greater_is_better=True,
    fp16=True,  # 若 GPU 支持
    logging_strategy="steps",
    logging_steps=100,
    save_total_limit=3,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# 训练
trainer.train()

# 验证/测试并打印详细报告
print("Eval on validation:")
val_res = trainer.evaluate(tokenized_datasets["validation"])
print(val_res.get("clf_report"))

print("Test:")
test_pred = trainer.predict(tokenized_datasets["test"])
preds = np.argmax(test_pred.predictions, axis=-1)
print(classification_report(tokenized_datasets["test"]["label"], preds, target_names=label_list, digits=4))
print("Confusion matrix:")
print(confusion_matrix(tokenized_datasets["test"]["label"], preds))

# 保存模型和 tokenizer（Trainer.save_model 已保存）
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# 简单推理示例函数
def predict_texts(texts):
    enc = tokenizer(texts, truncation=True, padding=True, max_length=MAX_LENGTH, return_tensors="pt")
    enc = {k: v.to(trainer.args.device) for k,v in enc.items()}
    model.to(trainer.args.device)
    with torch.no_grad():
        out = model(**enc)
        logits = out.logits.cpu().numpy()
    preds = np.argmax(logits, axis=-1)
    return [id2label[int(p)] for p in preds]

# 若需单独加载模型进行推理：
# from transformers import AutoModelForSequenceClassification, AutoTokenizer
# tokenizer = AutoTokenizer.from_pretrained(OUTPUT_DIR)
# model = AutoModelForSequenceClassification.from_pretrained(OUTPUT_DIR)
