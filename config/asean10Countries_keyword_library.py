from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass


# ==================== 常量定义 ====================

class Domain(Enum):
    """农业领域枚举"""
    PLANTING = 1  # 种植业
    ANIMAL_HUSBANDRY = 2  # 畜牧业
    FISHERY = 3  # 渔业（水产业）
    FACILITY_AGRICULTURE = 4  # 设施农业
    PROCESSING = 5  # 农产品加工业
    TRADE = 6  # 农产品贸易业
    TECH_SERVICE = 7  # 农业科技服务业
    RURAL_TOURISM = 8  # 休闲农业与乡村旅游业
    AGRICULTURE_CULTURE = 9  # 农业文化
    VOCATIONAL_EDU = 10  # 农业职业教育
    OTHER = 11  # 其它


# 领域中文名称映射（保持中文输出，便于理解）
DOMAIN_NAMES = {
    Domain.PLANTING: "种植业",
    Domain.ANIMAL_HUSBANDRY: "畜牧业",
    Domain.FISHERY: "渔业（水产业）",
    Domain.FACILITY_AGRICULTURE: "设施农业",
    Domain.PROCESSING: "农产品加工业",
    Domain.TRADE: "农产品贸易业",
    Domain.TECH_SERVICE: "农业科技服务业",
    Domain.RURAL_TOURISM: "休闲农业与乡村旅游业",
    Domain.AGRICULTURE_CULTURE: "农业文化",
    Domain.VOCATIONAL_EDU: "农业职业教育",
    Domain.OTHER: "其它"
}


@dataclass
class KeywordSet:
    """关键词集合"""
    core_words: List[str]  # 核心词，权重最高
    extension_words: List[str]  # 扩展词，权重中等
    context_words: List[str]  # 上下文词，需要上下文验证
    exclusion_words: List[str]  # 排除词，出现则降权
    required_words: List[str]  # 必须词，某些领域需要特定词确认


@dataclass
class ClassificationResult:
    """分类结果"""
    domain_id: int
    domain_name: str
    confidence: float
    keywords_found: List[str]
    evidence: Dict[str, Any]
    is_other: bool


# ==================== 越南语关键词库定义 ====================
def build_keyword_library() -> Dict[Domain, KeywordSet]:
    """构建扩充后的农业领域关键词库（越南语），覆盖更多短语与机构/法规/贸易词汇"""
    return {
        # 1. 种植业
        Domain.PLANTING: KeywordSet(
            # 核心栽培活动与作物体系
            core_words=[
                "trồng", "cây", "lúa", "canh tác", "giống"
                # 基础领域词
                "trồng trọt", "canh tác", "sản xuất cây trồng", "nghề trồng trọt",
                "ngành trồng trọt", "hệ thống canh tác", "hệ thống cây trồng",

                # 主要作物类别
                "cây trồng", "cây lương thực", "cây thực phẩm", "cây công nghiệp",
                "cây ăn quả", "cây rau màu", "cây hoa màu", "cây dược liệu",
                "cây lâm nghiệp (trồng rừng sản xuất)",

                # 具体主要作物
                # 粮食作物
                "lúa", "lúa nước", "lúa cạn", "lúa mùa", "lúa vụ đông xuân",
                "ngô", "bắp", "khoai lang", "khoai tây", "sắn", "khoai mì",
                "đậu", "đậu tương", "đậu nành", "đậu xanh", "đậu đen", "đậu phộng",
                "lúa mì", "lúa mạch",
                # 经济/工业作物
                "cà phê", "ca cao", "chè", "trà", "cao su", "mía", "dừa",
                "hồ tiêu", "tiêu", "điều", "cây có múi", "cam", "chanh", "bưởi",
                "chuối", "xoài", "nhãn", "vải", "sầu riêng", "thanh long",
                "dứa", "măng cụt", "chôm chôm",
                # 蔬菜与花卉
                "rau", "rau ăn lá", "rau ăn quả", "rau ăn củ",
                "cải", "cà chua", "dưa chuột", "ớt", "hành", "tỏi",
                "hoa", "hoa cắt cành", "hoa lan", "hoa hồng", "hoa cúc",

                # 种子与种苗
                "hạt giống", "giống cây trồng", "cây giống", "mầm giống",
                "giống địa phương", "giống thuần", "giống lai", "giống cải tiến",
                "vườn ươm", "vườn giống", "cây con", "mạ", "hom giống",

                # 补充高价值/特色经济作物
                "macca", "hồ đào", "ô liu", "hạt dẻ",
                "cây dược liệu quý", "sâm", "nấm linh chi", "đương quy",
                "cây cảnh", "bonsai", "cây công trình",

                # 补充具体果蔬品种（扩大覆盖面）
                "cà tím", "bí đao", "bí ngô", "su su", "đậu bắp", "rau muống",
                "bơ", "ổi", "mít", "mãng cầu", "khế", "cóc", "me",
            ],

            # 扩展栽培技术、管理与投入品
            extension_words=[
                # 补充现代智慧农业技术
                "nhà kính thông minh", "cảm biến độ ẩm đất", "hệ thống tưới tự động hóa",
                "robot gieo hạt", "robot thu hoạch", "nông nghiệp dữ liệu lớn",
                "mô hình dự báo sâu bệnh", "canh tác theo biến đổi khí hậu",

                # 补充特定病害与防控（针对主要作物）
                "bệnh vàng lùn trên lúa", "bệnh khảm lá sắn", "bệnh chết nhanh trên hồ tiêu",
                "bệnh thán thư trên xoài", "rầy nâu", "sâu đục thân",
                "quản lý dịch hại dựa trên cảnh báo sớm",

                # 补充产后处理与初加工（连接加工业但属种植环节）
                "phân loại sau thu hoạch", "làm sạch nông sản", "xử lý bằng hơi nước nóng (hấp)",
                "bảo quản lạnh", "bao gói sơ bộ tại vườn",

                # 栽培技术与农事操作
                "làm đất", "cày", "bừa", "san phẳng", "lên luống",
                "gieo hạt", "gieo thẳng", "gieo sạ", "cấy", "cấy mạ",
                "trồng dày", "trồng thưa", "tỉa cây", "tỉa chồi",
                "vun gốc", "làm cỏ", "thu hoạch", "gặt", "hái", "đào củ",
                "sấy hạt", "phơi khô", "bảo quản sau thu hoạch",

                # 灌溉与水分管理
                "tưới tiêu", "tưới nước", "hệ thống tưới",
                "tưới nhỏ giọt", "tưới phun mưa", "tưới ngập", "tưới rãnh",
                "tiết kiệm nước", "quản lý nước", "thoát nước", "tiêu úng",

                # 土壤与肥料管理
                "đất canh tác", "đất trồng trọt", "phân tích đất", "độ phì nhiêu",
                "cải tạo đất", "bón vôi", "bón phân", "phân bón",
                "phân hóa học", "phân đạm", "phân lân", "phân kali", "phân NPK",
                "phân hữu cơ", "phân chuồng", "phân xanh", "phân vi sinh",
                "phân bón lá", "bón thúc", "bón lót", "luân canh", "luân canh cây trồng",
                "xen canh", "trồng xen", "đa canh",

                # 植物保护
                "bảo vệ thực vật", "quản lý dịch hại", "sâu bệnh",
                "côn trùng gây hại", "bệnh cây", "cỏ dại",
                "thuốc bảo vệ thực vật", "thuốc trừ sâu", "thuốc trừ bệnh", "thuốc trừ cỏ",
                "quản lý dịch hại tổng hợp IPM", "kiểm soát sinh học",
                "thiên địch", "bẫy bả", "giống kháng bệnh",

                # 现代农业技术
                "cơ giới hóa trồng trọt", "máy cày", "máy gặt", "máy gặt đập liên hợp",
                "nông nghiệp chính xác", "bản đồ năng suất", "cảm biến đất",
                "ứng dụng drone trong trồng trọt", "phun thuốc bằng drone",
                "hệ thống canh tác thông minh",

                # 生产力与可持续性
                "năng suất", "sản lượng", "năng suất sinh học", "chỉ số thu hoạch",
                "thâm canh", "thâm canh bền vững", "canh tác bảo tồn",
                "trồng trọt thích ứng với biến đổi khí hậu",
                "giống chịu hạn", "giống chịu mặn",
            ],

            # 相关背景、经济、政策与生态系统
            context_words=[
                # 补充全球价值链与认证
                "chuỗi giá trị nông sản toàn cầu", "tiêu chuẩn GlobalGAP",
                "nông nghiệp thương mại", "hợp đồng liên kết tiêu thụ",

                # 补充资源管理与生态
                "quản lý dinh dưỡng tổng hợp", "sử dụng nước hiệu quả",
                "nông lâm kết hợp", "trồng cây chắn gió, cải tạo đất",

                # 经济与市场
                "thị trường nông sản", "giá lúa", "giá cà phê", "giá cao su",
                "cung cầu nông sản", "xuất khẩu gạo", "xuất khẩu cà phê",
                "liên kết sản xuất", "hợp tác xã nông nghiệp",

                # 政策与规划
                "chiến lược phát triển trồng trọt", "quy hoạch vùng cây trồng",
                "chính sách hỗ trợ nông dân", "chính sách giá nông sản",
                "an ninh lương thực", "an toàn thực phẩm",

                # 农业生态与可持续性
                "hệ sinh thái nông nghiệp", "đa dạng sinh học nông nghiệp",
                "nông nghiệp sinh thái", "nông nghiệp tái sinh",
                "bảo tồn tài nguyên đất", "bảo vệ nguồn nước",
                "nông nghiệp hữu cơ", "chứng nhận hữu cơ",
                "nông nghiệp tuần hoàn",

                # 研究与推广
                "nghiên cứu giống cây trồng", "khảo nghiệm giống",
                "chuyển giao tiến bộ kỹ thuật", "khuyến nông",
                "phòng thí nghiệm chẩn đoán bệnh cây",

                # 气候变化与风险
                "rủi ro thời tiết", "hạn hán", "ngập mặn", "xâm nhập mặn",
                "thời tiết cực đoan", "bảo hiểm nông nghiệp",
            ],

            # 明确排除的非相关领域
            exclusion_words=[
                # 畜牧业
                "chăn nuôi", "gia súc", "gia cầm", "thức ăn chăn nuôi",
                # 水产养殖
                "nuôi trồng thủy sản", "đánh bắt cá", "tôm", "cá",
                # 加工与贸易（虽有关联但非种植核心）
                "nhà máy chế biến nông sản", "chế biến sâu",
                "thương mại nông sản", "xuất nhập khẩu (作为主要焦点时)",
                # 其他无关领域
                "lâm nghiệp tự nhiên", "bảo tồn rừng nguyên sinh",
                "du lịch nông nghiệp", "kiến trúc cảnh quan",
            ],

            # 必需词根 - 确保核心领域相关性
            required_words=[]
        ),

        # 2. 畜牧业
        Domain.ANIMAL_HUSBANDRY: KeywordSet(
            # 核心养殖活动、品种与设施
            core_words=[
                # 基础领域词
                "chăn nuôi", "ngành chăn nuôi", "sản xuất chăn nuôi", "chăn nuôi động vật",
                "chăn nuôi gia súc", "chăn nuôi gia cầm", "chăn nuôi vật nuôi khác",

                # 主要畜禽品种
                # 家畜
                "lợn", "heo", "bò", "bò thịt", "bò sữa", "trâu", "dê", "cừu", "ngựa", "thỏ",
                # 家禽
                "gà", "gà thịt", "gà đẻ trứng", "vịt", "vịt thịt", "vịt đẻ trứng", "ngan", "ngỗng",
                "gà tây", "chim cút", "bồ câu",
                # 特种养殖
                "hươu", "nai", "đà điểu", "lợn rừng", "dúi", "cầy hương",

                # 生产设施与场所
                "trại chăn nuôi", "trang trại chăn nuôi", "chuồng trại", "chuồng nuôi",
                "trại lợn", "trại gà", "trại bò sữa", "vùng chăn nuôi", "khu chăn nuôi tập trung",
                "chuồng kín", "chuồng hở", "hệ thống chuồng nuôi tự động hóa",

                # 饲料与营养
                "thức ăn chăn nuôi", "cám", "thức ăn hỗn hợp", "thức ăn tinh", "thức ăn thô xanh",
                "nguồn thức ăn", "nguyên liệu thức ăn", "phụ phẩm nông nghiệp làm thức ăn",

                # 产品
                "thịt", "trứng", "sữa", "thịt lợn", "thịt gà", "thịt bò", "trứng gà", "sữa bò",
                "da", "lông", "phân bón từ chất thải chăn nuôi",

                "chăn nuôi", "gia súc", "gia cầm", "lợn", "bò", "gà",
                # 补充重要品种（完善覆盖）
                "bê", "nghé", "lợn con", "gà con", "vịt con",  # 幼畜/禽术语
                "cừu lấy lông", "dê sữa", "thỏ thịt",  # 细分用途品种
                "ong", "tằm",  # 特种经济动物（虽小但属畜牧业范畴）

                # 补充核心设施与环节
                "khu cách ly", "phòng thí nghiệm chẩn đoán thú y",
                "trại ươm giống", "trại vỗ béo",
            ],

            # 扩展技术、管理、健康、加工与可持续发展
            extension_words=[
                # 补充现代养殖技术与模式
                "chăn nuôi tuần hoàn", "chăn nuôi theo đàn", "quản lý đàn bằng phần mềm ERP",
                "chuồng nuôi tiêu chuẩn", "hệ thống kiểm soát vi khí hậu",
                "sử dụng hormone tăng trưởng", "cấy ghép phôi bò",

                # 补充具体疾病名称（提高识别率）
                "bệnh dịch tả lợn cổ điển", "bệnh viêm da nổi cục", "bệnh lở mồm long móng type O",
                "bệnh cầu trùng", "bệnh tụ huyết trùng", "bệnh bại liệt ở gà",
                "hội chứng rối loạn hô hấp và sinh sản (PRRS)",

                # 补充饲料与营养细分
                "thức ăn hỗn hợp hoàn chỉnh", "thức ăn cho gà đẻ", "thức ăn cho heo nái",
                "bổ sung axit amin", "phụ gia thức ăn", "chất kích thích tăng trưởng",

                # 补充质量与追溯技术
                "đeo thẻ tai (tagging)", "chip điện tử", "hệ thống giám sát xuất chuồng",
                "kiểm tra tồn dư thuốc thú y", "giấy chứng nhận kiểm dịch",

                # 育种与遗传改良
                "giống vật nuôi", "con giống", "đàn giống", "công tác giống",
                "nhân giống", "chọn lọc giống", "lai giống", "cải tạo giống",
                "giống thuần", "giống lai", "giống địa phương", "giống nhập ngoại",
                "công nghệ sinh sản", "thụ tinh nhân tạo", "cấy phôi",

                # 饲养管理与营养技术
                "kỹ thuật chăn nuôi", "quy trình chăn nuôi", "chăn nuôi công nghiệp",
                "chăn nuôi bán công nghiệp", "chăn nuôi hộ gia đình", "chăn nuôi trang trại",
                "chăn nuôi theo hướng hữu cơ", "chăn nuôi sinh thái",
                "thức ăn viên", "thức ăn đậm đặc", "premix", "khẩu phần ăn",
                "bổ sung vitamin", "bổ sung khoáng chất", "chất điều hòa sinh trưởng",
                "men vi sinh", "enzyme tiêu hóa",

                # 动物健康与兽医
                "thú y", "phòng bệnh", "vaccine", "vắc xin", "tiêm phòng", "lịch tiêm phòng",
                "bệnh truyền nhiễm", "dịch bệnh", "cúm gia cầm", "lở mồm long móng",
                "tai xanh", "dịch tả lợn châu Phi", "bệnh newcastle",
                "kháng sinh", "sử dụng kháng sinh có trách nhiệm", "kháng kháng sinh",
                "chẩn đoán bệnh", "điều trị bệnh", "cách ly đàn",
                "an toàn sinh học", "vệ sinh chuồng trại", "sát trùng",

                # 设施与环境控制
                "hệ thống làm mát", "hệ thống thông gió", "hệ thống sưởi ấm",
                "hệ thống cho ăn tự động", "hệ thống uống nước tự động",
                "hệ thống thu gom và xử lý chất thải", "hầm biogas",
                "xử lý nước thải chăn nuôi", "ủ phân compost",

                # 屠宰与加工
                "giết mổ", "lò mổ", "giết mổ tập trung", "giết mổ gia đình",
                "vận chuyển vật nuôi sống", "bảo quản thịt", "chế biến thịt",
                "sản phẩm từ sữa", "chế biến sữa", "sản phẩm từ trứng",

                # 质量、安全与认证
                "an toàn thực phẩm", "kiểm soát chất lượng", "truy xuất nguồn gốc",
                "kiểm tra dư lượng kháng sinh", "kiểm tra hormone",
                "chứng nhận VietGAHP", "chứng nhận GlobalGAP cho chăn nuôi",
                "chứng nhận hữu cơ", "chứng nhận thân thiện với động vật",
                "chăn nuôi không sử dụng kháng sinh",
            ],

            # 相关背景、经济、政策与发展
            context_words=[
                # 补充产业链与价值链
                "liên kết chuỗi từ trang trại đến bàn ăn", "hợp đồng chăn nuôi",
                "bao tiêu sản phẩm", "công nghiệp chế biến thịt",

                # 补充社会经济影响
                "xóa đói giảm nghèo thông qua chăn nuôi", "tạo việc làm nông thôn",
                "phát triển chăn nuôi quy mô nhỏ",

                # 经济与市场
                "thị trường chăn nuôi", "giá thức ăn chăn nuôi", "giá thịt",
                "cung cầu thịt", "nhập khẩu thịt", "xuất khẩu thịt",
                "chuỗi giá trị chăn nuôi", "liên kết sản xuất",

                # 政策与管理
                "chiến lược phát triển chăn nuôi", "quy hoạch vùng chăn nuôi",
                "chính sách hỗ trợ chăn nuôi", "phát triển chăn nuôi bền vững",
                "kiểm soát dịch bệnh động vật", "Luật Thú y", "Luật Chăn nuôi",

                # 可持续发展
                "giảm phát thải từ chăn nuôi", "biến đổi khí hậu và chăn nuôi",
                "quản lý chất thải chăn nuôi", "kinh tế tuần hoàn trong chăn nuôi",
                "phúc lợi động vật", "chăn nuôi có trách nhiệm",

                # 研究与技术
                "nghiên cứu chăn nuôi", "chuyển giao công nghệ chăn nuôi",
                "ứng dụng công nghệ cao trong chăn nuôi", "chăn nuôi thông minh",
                "IoT trong chăn nuôi", "quản lý đàn bằng phần mềm",

                # 相关领域
                "trồng trọt (cung cấp thức ăn)", "công nghiệp thức ăn chăn nuôi",
                "thú y cộng đồng", "sức khỏe động vật và sức khỏe con người",
            ],

            # 明确排除的非相关领域
            exclusion_words=[
                # 水产养殖
                "nuôi trồng thủy sản", "đánh bắt cá", "ngư nghiệp", "tôm", "cá",
                # 植物种植
                "trồng lúa", "trồng ngô", "trồng rau", "cây công nghiệp",
                # 其他无关领域
                "săn bắn", "động vật hoang dã (không thuần hóa)",
                "thú cưng", "động vật cảnh", "động vật trong sở thú",
                "thực phẩm chay/thuần chay", "công nghiệp da giày (trừ nguồn cung)",
            ],

            # 必需词根 - 确保核心领域相关性
            required_words=[]
        ),

        # 3. 渔业（水产业） — 扩充重点
        Domain.FISHERY: KeywordSet(
            # 核心概念、品种、机构、法规与项目
            core_words=[
                # 基础领域词
                "thủy sản", "hải sản", "ngư nghiệp", "khai thác thủy sản", "đánh bắt",
                "nuôi trồng thủy sản", "thủy sản nước ngọt", "thủy sản nước mặn",

                # 从业者与设施
                "ngư dân", "tàu cá", "cảng cá", "chợ cá", "bến cá", "cơ sở nuôi trồng thủy sản",
                "lồng bè nuôi", "ao nuôi", "trại giống thủy sản", "nhà máy chế biến thủy sản",

                # 管理、资源与机构
                "nguồn lợi thủy sản", "trữ lượng thủy sản", "Cục Thuỷ sản", "Cục Kiểm ngư",
                "Tổng cục Thuỷ sản", "VASEP", "Hiệp hội Chế biến và Xuất khẩu Thủy sản",

                # 重要国际机构与法规（缩写与全称）
                "NOAA", "Cơ quan Quản lý Khí quyển và Đại dương Quốc gia",
                "DOC", "Bộ Thương mại Hoa Kỳ", "MMPA", "Đạo luật Bảo vệ Động vật có vú Biển",
                "IUU", "Đánh bắt bất hợp pháp, không báo cáo và không theo quy định",
                "SIMP", "Chương trình Giám sát Nhập khẩu Thủy sản",
                "FIP", "Dự án Cải thiện Nghề cá",

                # 主要品种（捕捞与养殖）
                # 鱼类
                "cá", "cá ngừ", "cá tra", "cá basa", "cá hồi", "cá rô phi", "cá chép",
                "cá thu", "cá nục", "cá mòi", "cá đối", "cá bớp", "cá chim",
                "cá kiếm", "cá ngừ vây xanh", "cá ngừ vằn",
                # 甲壳类
                "tôm", "tôm sú", "tôm thẻ", "tôm hùm", "tôm càng xanh",
                "cua", "cua biển", "cua đá", "ghẹ",
                # 软体动物与其他
                "mực", "mực ống", "mực nang", "bạch tuộc",
                "ngao", "sò", "nghêu", "hàu", "ốc", "trai", "vẹm",
                # 其他水产资源
                "rong biển", "tảo", "cầu gai", "hải sâm",

                # 产品与加工形态
                "sản phẩm thủy sản", "thủy sản đông lạnh", "thủy sản tươi sống",
                "thủy sản khô", "thủy sản đóng hộp", "thủy sản hun khói",
                "thủy sản", "hải sản", "ngư", "cá", "tôm",
                # 补充具体品种（尤其是高价值或新兴养殖品种）
                "cá mú", "cá tầm", "cá chẽm", "cá lăng", "cá lóc", "cá trắm", "cá mè",
                "tôm càng đỏ", "tôm thẻ chân trắng", "tôm rảo",
                "cua lột", "cua gạch", "cua hoàng đế",
                "sá sùng", "tu hài", "bào ngư", "sứa",

                # 补充产品形态（预制菜、即食产品等趋势）
                "thủy sản chế biến sẵn", "thủy sản ăn liền", "surimi",
                "chả cá", "viên cá", "bột cá", "dầu cá",
            ],

            # 扩展技术、管理、贸易、认证与追溯
            extension_words=[
                # 捕捞技术与管理
                "tàu cá vỏ thép", "tàu cá vỏ gỗ", "lưới kéo", "lưới vây", "lưới rê",
                "ngư cụ", "hạn ngạch đánh bắt", "mùa vụ đánh bắt", "vùng khai thác",
                "thiết bị giám sát hành trình tàu cá", "vùng đánh bắt cấm/tạm thời",

                # 养殖技术与疾病
                "thức ăn thủy sản", "con giống", "nuôi thâm canh", "nuôi bán thâm canh",
                "nuôi quảng canh", "nuôi sinh thái", "bệnh thủy sản",
                "đốm trắng trên tôm", "hoại tử gan tụy cấp", "hội chứng EMS",
                "vaccine cho thủy sản", "kháng sinh trong nuôi trồng",

                # 认证与可持续性
                "chứng nhận MSC", "Hội đồng Quản lý Biển", "chứng nhận ASC",
                "Hội đồng Quản lý Nuôi trồng Thủy sản", "chứng nhận GlobalGAP cho thủy sản",
                "chứng nhận BAP", "Thực hành Nuôi trồng Tốt nhất",
                "chứng nhận hữu cơ cho thủy sản",

                # 追溯与质量控制
                "truy xuất nguồn gốc thủy sản", "nhật ký khai thác",
                "sổ theo dõi nuôi trồng", "kiểm dịch thủy sản",
                "kiểm tra dư lượng kháng sinh", "kiểm tra kim loại nặng",
                "kiểm nghiệm histamine", "giám sát an toàn thực phẩm",

                # 贸易与物流
                "xuất khẩu thủy sản", "nhập khẩu thủy sản",
                "thị trường xuất khẩu thủy sản", "thị trường EU", "thị trường Mỹ", "thị trường Nhật",
                "thuế chống bán phá giá thủy sản", "rào cản kỹ thuật thương mại",
                "dừng nhập khẩu thủy sản", "cảnh báo nhập khẩu",
                "giấy chứng nhận xuất xứ CO", "giấy phép khai thác",
                "vận tải lạnh thủy sản", "container lạnh", "bao gói chân không",

                # 数据与统计
                "sản lượng khai thác", "sản lượng nuôi trồng", "diện tích mặt nước nuôi",
                "trữ lượng khai thác bền vững", "sức tải môi trường vùng nuôi",

                # 补充新兴养殖模式与技术
                "nuôi tuần hoàn khép kín (RAS)", "nuôi sinh học floc (biofloc)",
                "nuôi kết hợp đa bậc (IMTA)", "nuôi trong hệ thống lồng ngoài khơi",
                "tôm sinh thái - lúa", "cá - lúa kết hợp",

                # 补充市场与消费趋势
                "thủy sản có chứng nhận", "thủy sản địa phương", "thủy sản mùa vụ",
                "khai thác thủ công", "khai thác quy mô nhỏ",
                "tiêu thụ thủy sản bền vững", "nhãn sinh thái (ecolabel)",

                # 补充具体病害与健康管理
                "bệnh đốm đen trên tôm", "bệnh phân trắng", "hội chứng tử vong sớm (EMS)",
                "bệnh hoại tử thần kinh trên cá", "ký sinh trùng (rận biển, sán lá)",
                "quản lý sức khỏe tổng hợp (health management)",
            ],

            # 相关背景、生态系统与发展政策
            context_words=[
                # 生态系统与栖息地
                "biển", "đại dương", "sông", "hồ", "ao", "đầm phá", "vùng cửa sông",
                "rạn san hô", "rừng ngập mặn", "thảm cỏ biển", "vùng đất ngập nước",

                # 管理与发展
                "quản lý nghề cá", "quản lý ngư trường", "quản lý tàu cá",
                "quy hoạch vùng nuôi trồng thủy sản", "phát triển ngư nghiệp bền vững",
                "khai thác bền vững", "nuôi trồng có trách nhiệm",

                # 保护与保育
                "bảo tồn nguồn lợi thủy sản", "bảo vệ môi trường biển",
                "khu bảo tồn biển", "tái tạo nguồn lợi", "thả giống tái tạo",
                "chống khai thác quá mức", "đa dạng sinh học thủy sinh",

                # 政策与战略
                "Luật Thủy sản", "Chiến lược phát triển thủy sản",
                "chính sách hỗ trợ ngư dân", "an sinh xã hội cho ngư dân",
                "ứng phó với biến đổi khí hậu cho ngư nghiệp",
                "nông nghiệp - ngư nghiệp kết hợp",

                # 经济与安全
                "kinh tế biển", "an ninh lương thực từ thủy sản",
                "an toàn lao động trên biển", "tìm kiếm cứu nạn ngư dân",
                # 补充气候变化与适应
                "axit hóa đại dương", "nước biển dâng", "xâm nhập mặn ảnh hưởng nuôi trồng",
                "hiện tượng tẩy trắng san hô", "thời tiết cực đoan ảnh hưởng nghề cá",

                # 补充社会经济层面
                "quyền tiếp cận nguồn lợi", "quản lý nghề cá cộng đồng",
                "phụ nữ trong ngư nghiệp", "di cư nghề cá",
            ],

            # 明确排除的非相关领域
            exclusion_words=[
                # 陆生农业
                "trồng trọt", "cây lương thực", "cây công nghiệp",
                "chăn nuôi gia súc", "chăn nuôi gia cầm",
                # 其他不相关领域
                "du lịch biển (tắm biển, lặn giải trí)",  # 与生产性渔业区分
                "công nghiệp đóng tàu (trừ tàu cá)",  # 船舶制造
                "dầu khí ngoài khơi",  # 海上油气
                "hàng hải thương mại",  # 商业航运
                # 防止与消费端烹饪内容混淆
                "cách nấu", "công thức", "món ăn", "chế biến món",
                "nhà hàng hải sản", "ẩm thực biển",
            ],

            # 必需词根 - 确保核心领域相关性
            required_words=[]
        ),

        # 4. 设施农业
        Domain.FACILITY_AGRICULTURE: KeywordSet(
            core_words=[
                "nhà kính", "nhà màng", "nhà lưới", "nông nghiệp công nghệ cao",
                "thủy canh", "khí canh", "trồng trọt không cần đất", "nông nghiệp kiểm soát",
                # 补充核心设施与系统类型
                "trang trại trong nhà", "nông nghiệp đô thị trong nhà",
                "hệ thống canh tác khép kín", "trang trại container",
                "nông nghiệp đa tầng", "vườn thẳng đứng",
                # 补充核心栽培方式
                "bán thủy canh", "trồng trên giá thể", "giá thể trồng trọt",
                "nhà kính", "thủy canh", "công nghệ cao", "kiểm soát",
                "trồng trọt truyền thống", "đồng ruộng", "đất canh tác ngoài trời",

            ],
            extension_words=[
                "kỹ thuật nhà kính", "kiểm soát môi trường", "hệ thống tưới", "điều khiển tự động",
                "IoT nông nghiệp", "ánh sáng LED trồng trọt", "trang trại thẳng đứng",
                # 补充环境控制技术
                "hệ thống kiểm soát nhiệt độ", "hệ thống kiểm soát độ ẩm",
                "hệ thống thông gió nhà kính", "hệ thống che bóng tự động",
                "kiểm soát nồng độ CO2", "màng phủ nhà kính thông minh",
                # 补充种植与灌溉技术
                "hệ thống tưới nhỏ giọt", "hệ thống tưới phun sương",
                "hệ thống dinh dưỡng tuần hoàn", "dung dịch thủy canh",
                "giá thể xơ dừa", "giá thể đá trân châu", "giá thể vermiculite",
                # 补充自动化与智能化
                "cảm biến môi trường cây trồng", "hệ thống giám sát từ xa",
                "robot thu hoạch trong nhà kính", "AI tối ưu điều kiện tăng trưởng",
                "phần mềm quản lý trang trại nhà kính",
                # 补充能源与可持续性
                "năng lượng mặt trời cho nhà kính", "hệ thống thu hồi nhiệt thải",
                "nông nghiệp tuần hoàn trong nhà",
            ],
            context_words=[
                "nông nghiệp hiện đại", "nông nghiệp đô thị", "sản xuất sạch",
                # 补充发展理念与优势
                "sản xuất quanh năm", "tiết kiệm nước và phân bón",
                "giảm thiểu thuốc bảo vệ thực vật", "năng suất cao trên diện tích nhỏ",
                "sản phẩm an toàn, sạch", "giảm phụ thuộc thời tiết",
                # 补充政策与技术背景
                "nông nghiệp 4.0", "cách mạng xanh 2.0",
                "ứng phó biến đổi khí hậu", "an ninh lương thực đô thị",
                "đầu tư hạ tầng nông nghiệp hiện đại",
            ],
            exclusion_words=[],
            required_words=[]
        ),

        # 5. 农产品加工业
        Domain.PROCESSING: KeywordSet(
            # 核心加工活动与产业类型
            core_words=[
                "chế biến nông sản",  # 农产品加工
                "chế biến thực phẩm nông sản",  # 农产品食品加工
                "chế biến thủy sản",  # 水产品加工
                "chế biến thịt",  # 肉类加工
                "chế biến rau quả",  # 果蔬加工
                "chế biến lúa gạo",  # 稻米加工
                "chế biến cà phê",  # 咖啡加工
                "chế biến hạt điều",  # 腰果加工
                "chế biến cao su",  # 橡胶加工
                "xử lý sau thu hoạch",  # 采后处理
                "chế biến sâu nông sản",  # 农产品深加工
                "tinh chế nông sản",  # 农产品精制
                "nhà máy chế biến nông sản",  # 农产品加工厂
                "nhà máy chế biến thủy sản",  # 水产品加工厂
                "dây chuyền chế biến nông sản",  # 农产品加工流水线
                "công nghệ chế biến nông sản",  # 农产品加工技术
                "đóng gói nông sản",  # 农产品包装
                "bao bì nông sản",  # 农产品包装材料
                # 补充关键加工环节与新兴业态
                "sơ chế nông sản",  # 农产品预处理（采后关键第一步）
                "phân loại và đánh giá chất lượng",  # 分级分选
                "chế biến thức ăn chăn nuôi",  # 饲料加工（重要关联产业）
                "chế biến tinh bột",  # 淀粉加工
                "chế biến đường",  # 制糖
                "xưởng chế biến thủ công",  # 手工作坊（涵盖小规模加工）
                "nhà máy đồ hộp",  # 罐头厂

            ],

            # 扩展加工技术、工艺与质量管理
            extension_words=[
                # 补充前沿加工技术
                "công nghệ cao áp (HPP)",  # 超高压加工
                "xử lý bằng xung điện (PEF)",  # 脉冲电场处理
                "sấy phun",  # 喷雾干燥
                "cô đặc chân không",  # 真空浓缩
                "thẩm thấu ngược",  # 反渗透
                "ép lạnh",  # 冷榨
                "oxy hóa nhiệt độ cao (UHT)",  # 超高温处理（补充全称）

                # 补充具体产品加工
                "sản xuất bột ngọt (mì chính)",  # 味精生产
                "chế biến ca cao thành chocolate",  # 巧克力加工
                "sản xuất bia từ lúa mạch",  # 啤酒酿造
                "làm phô mai",  # 奶酪制作
                "sản xuất giò chả",  # 肉糜制品加工（越南特色）

                # 补充质量管理与数字化
                "hệ thống truy xuất nguồn gốc điện tử",  # 电子溯源系统
                "cảm biến theo dõi nhiệt độ, độ ẩm trong kho",  # 仓储温湿度监控
                "phần mềm quản lý sản xuất (MES)",  # 制造执行系统
                "blockchain trong truy xuất nguồn gốc thực phẩm",  # 区块链食品溯源

                # 补充副产物综合利用
                "sản xuất nhiên liệu sinh học (biofuel)",  # 生物燃料生产
                "chiết xuất pectin từ phụ phẩm trái cây",  # 果胶提取
                "sản xuất thức ăn gia súc từ bã ép",  # 饲料生产

                # 加工技术与方法
                "đông lạnh nhanh IQF",  # 速冻
                "sấy khô nông sản",  # 农产品干燥
                "sấy thăng hoa",  # 冷冻干燥
                "tiệt trùng UHT",  # 超高温灭菌
                "thanh trùng",  # 巴氏杀菌
                "lên men thực phẩm",  # 食品发酵
                "muối chua",  # 腌渍
                "hun khói",  # 烟熏
                "đóng hộp nông sản",  # 农产品罐装
                "chiết rót vô trùng",  # 无菌灌装
                "ép dầu thực vật",  # 植物油压榨
                "tinh luyện dầu ăn",  # 食用油精炼

                # 质量控制与认证
                "HACCP trong chế biến nông sản",  # 农产品加工中的HACCP
                "ISO 22000 cho nhà máy chế biến",  # 加工厂的ISO 22000
                "FSSC 22000",  # 食品安全体系认证
                "BRCGS",  # 英国零售商协会标准
                "IFS Food",  # 国际食品标准
                "kiểm soát vi sinh trong chế biến",  # 加工中的微生物控制
                "kiểm soát nhiệt độ và độ ẩm",  # 温湿度控制
                "quản lý chất lượng toàn diện TQM",  # 全面质量管理
                "quy trình vệ sinh SSOP",  # 卫生标准操作程序
                "kiểm tra dư lượng thuốc bảo vệ thực vật",  # 农药残留检测

                # 设备与生产线
                "máy móc chế biến nông sản",  # 农产品加工机械
                "dây chuyền đóng gói tự động",  # 自动包装线
                "hệ thống phân loại theo màu sắc",  # 色选系统
                "máy rửa và chần rau quả",  # 果蔬清洗漂烫机
                "hệ thống cấp đông băng chuyền",  # 传送带冻结系统
                "phòng lạnh bảo quản",  # 冷藏库
                "kho mát bảo quản",  # 保鲜库

                # 创新与增值
                "chế biến tạo sản phẩm giá trị gia tăng",  # 高附加值产品加工
                "tận dụng phụ phẩm nông nghiệp",  # 农业副产品利用
                "sản xuất thực phẩm chức năng từ nông sản",  # 农产品功能食品生产
                "chiết xuất hợp chất sinh học từ nông sản",  # 农产品生物活性成分提取
                "công nghệ chế biến ít làm biến đổi thực phẩm",  # 食品非热加工技术
                "đóng gói thông minh cho nông sản",  # 农产品智能包装
                "công nghệ MAP đóng gói khí quyển biến đổi",  # 气调包装技术
            ],

            # 相关背景、产业链与政策
            context_words=[
                # 补充产业经济与创新
                "công nghiệp chế biến thực phẩm",  # 食品加工业（更广泛范畴）
                "đổi mới sáng tạo trong chế biến",  # 加工创新
                "chuyển đổi số nhà máy chế biến",  # 加工厂数字化转型
                "hợp tác công tư (PPP) trong chế biến",  # 公私合作

                # 补充可持续性
                "tiết kiệm năng lượng trong chế biến",  # 加工节能
                "xử lý và tái sử dụng nước thải",  # 废水处理回用
                "sản xuất sạch hơn",  # 清洁生产

                # 产业链与集群
                "cụm công nghiệp chế biến nông sản",  # 农产品加工产业集群
                "khu chế xuất thực phẩm",  # 食品加工出口区
                "liên kết chuỗi giá trị nông sản",  # 农产品价值链连接
                "từ trang trại đến bàn ăn",  # 从农场到餐桌
                "logistics lạnh cho chế biến",  # 加工冷链物流

                # 政策与发展
                "chính sách phát triển công nghiệp chế biến nông sản",  # 农产品加工业发展政策
                "quy hoạch vùng nguyên liệu cho chế biến",  # 加工原料区规划
                "đầu tư vào nhà máy chế biến hiện đại",  # 现代加工厂投资
                "chuyển giao công nghệ chế biến tiên tiến",  # 先进加工技术转移

                # 经济与市场
                "giá trị gia tăng từ chế biến",  # 加工增值
                "tỷ lệ chế biến nông sản",  # 农产品加工率
                "thị trường sản phẩm chế biến từ nông sản",  # 农产品加工制品市场
                "xuất khẩu sản phẩm chế biến từ nông sản",  # 农产品加工品出口
                "an toàn thực phẩm trong chế biến",  # 加工中的食品安全
                "chế biến", "nông sản", "nhà máy", "công nghệ"
            ],

            # 明确排除的非相关领域
            exclusion_words=[
                # 生产与种植
                "kỹ thuật trồng trọt",  # 种植技术
                "quy trình sản xuất nông nghiệp",  # 农业生产流程
                "chăm sóc cây trồng vật nuôi",  # 种养殖管理

                # 贸易与流通
                "thương mại nông sản thô",  # 初级农产品贸易
                "đấu giá nông sản",  # 农产品拍卖
                "vận chuyển nông sản thô",  # 初级农产品运输

                # 其他领域
                "du lịch nông nghiệp",  # 农业旅游
                "dịch vụ kiểm nghiệm nông sản",  # 农产品检测服务
                "nghiên cứu giống cây trồng",  # 作物品种研究
            ],

            # 必须包含的核心词根
            required_words=[]
        ),

        # 6. 农产品贸易业
        Domain.TRADE: KeywordSet(
            # 核心贸易活动与市场
            core_words=[
                # 补充贸易壁垒与争端
                "kiện chống bán phá giá",  # 反倾销诉讼
                "trợ cấp nông nghiệp (WTO)",  # 农业补贴（WTO框架下）
                "hàng rào vệ sinh dịch tễ (SPS)",  # 卫生与植物检疫措施
                "cấm vận thương mại",  # 贸易禁运
                "tranh chấp thương mại nông sản",  # 农产品贸易争端

                # 补充贸易金融与支付
                "tín dụng xuất khẩu nông sản",  # 农产品出口信贷
                "bảo hiểm tín dụng xuất khẩu",  # 出口信用保险
                "thanh toán quốc tế",  # 国际支付
                "tỷ giá hối đoái",  # 汇率

                # 补充新兴贸易模式
                "thương mại nông sản trực tuyến B2B",  # 农产品B2B在线贸易
                "xuất khẩu nông sản thông qua sàn thương mại điện tử",  # 通过电商平台出口农产品
                "thương mại nông sản bền vững",  # 可持续农产品贸易
                "chuỗi cung ứng ngắn",  # 短供应链

                # 补充具体产品贸易术语
                "gạo 5% tấm", "cà phê robusta", "cao su RSS3", "hạt điều W320",  # 具体产品规格
                "giá FOB cảng Sài Gòn", "giá CIF cảng Rotterdam",  # 具体价格术语

                # 补充具体贸易活动与主体
                "nhà phân phối nông sản",  # 农产品分销商
                "đại lý xuất nhập khẩu nông sản",  # 农产品进出口代理
                "sàn giao dịch nông sản",  # 农产品交易平台
                "đấu giá nông sản",  # 农产品拍卖
                "hợp đồng tương lai nông sản",  # 农产品期货合约

                # 补充重要市场（东南亚、新兴市场）
                "thị trường Hàn Quốc cho nông sản",  # 韩国农产品市场
                "thị trường ASEAN cho nông sản",  # 东盟农产品市场
                "thị trường Nga cho nông sản",  # 俄罗斯农产品市场
                "thị trường Trung Đông cho nông sản",  # 中东农产品市场

                "thương mại nông sản",  # 农产品贸易
                "xuất khẩu nông sản",  # 农产品出口
                "nhập khẩu nông sản",  # 农产品进口
                "thị trường nông sản",  # 农产品市场
                "thị trường xuất khẩu nông sản",  # 农产品出口市场
                "thương mại quốc tế nông sản",  # 国际农产品贸易
                "xuất khẩu thủy sản",  # 水产品出口
                "xuất khẩu gạo",  # 大米出口
                "xuất khẩu cà phê",  # 咖啡出口
                "xuất khẩu hạt điều",  # 腰果出口
                "xuất khẩu cao su",  # 橡胶出口
                "xuất khẩu trái cây",  # 水果出口
                "thị trường Hoa Kỳ cho nông sản",  # 美国农产品市场
                "thị trường EU cho nông sản",  # 欧盟农产品市场
                "thị trường Trung Quốc cho nông sản",  # 中国农产品市场
                "thị trường Nhật Bản cho nông sản",  # 日本农产品市场
                "bán hàng nông sản",  # 农产品销售
                "tiêu thụ nông sản",  # 农产品消费
            ],

            # 扩展贸易政策、流程与渠道
            extension_words=[
                # 补充宏观经济与地缘政治影响
                "toàn cầu hóa và thương mại nông sản",  # 全球化与农产品贸易
                "chiến tranh thương mại ảnh hưởng nông sản",  # 贸易战对农产品的影响
                "khủng hoảng logistic toàn cầu",  # 全球物流危机
                "cách mạng công nghiệp 4.0 và thương mại nông sản",  # 工业4.0与农产品贸易

                # 补充区域经济一体化
                "Khu vực Mậu dịch Tự do ASEAN (AFTA)",  # 东盟自由贸易区
                "Hiệp định Đối tác Toàn diện và Tiến bộ xuyên Thái Bình Dương (CPTPP)",  # 全面与进步跨太平洋伙伴关系协定
                "Liên minh Kinh tế Á-Âu (EAEU)",  # 欧亚经济联盟

                # 贸易政策与协议
                "hiệp định thương mại tự do cho nông sản",  # 农产品自由贸易协定
                "FTA ảnh hưởng đến nông sản",  # 影响农产品的自贸协定
                "EVFTA với nông sản",  # 越欧自贸协定中的农产品
                "CPTPP với nông sản",  # 跨太平洋伙伴关系协定中的农产品
                "rào cản kỹ thuật trong thương mại nông sản",  # 农产品贸易技术壁垒
                "rào cản phi thuế quan đối với nông sản",  # 农产品非关税壁垒
                "thuế chống bán phá giá nông sản",  # 农产品反倾销税
                "hạn ngạch xuất khẩu nông sản",  # 农产品出口配额
                "giá sàn xuất khẩu gạo",  # 大米出口底价

                # 贸易流程与单证
                "thủ tục hải quan cho nông sản",  # 农产品海关手续
                "giấy chứng nhận xuất xứ cho nông sản",  # 农产品原产地证书
                "CO form D/ form E",  # D表/E表原产地证
                "giấy phép xuất khẩu nông sản",  # 农产品出口许可证
                "kiểm dịch thực vật và động vật",  # 动植物检疫
                "chứng nhận vệ sinh an toàn thực phẩm xuất khẩu",  # 出口食品安全卫生证书
                "kiểm tra chất lượng nông sản xuất khẩu",  # 出口农产品质量检验

                # 贸易渠道与模式
                "thương mại điện tử nông sản",  # 农产品电子商务
                "xuất khẩu trực tiếp nông sản",  # 农产品直接出口
                "xuất khẩu uỷ thác nông sản",  # 农产品委托出口
                "kênh phân phối nông sản quốc tế",  # 国际农产品分销渠道
                "siêu thị nước ngoài nhập khẩu nông sản",  # 进口农产品的国外超市
                "nhà nhập khẩu nông sản",  # 农产品进口商
                "nhà xuất khẩu nông sản",  # 农产品出口商

                # 物流与供应链
                "logistics nông sản xuất khẩu",  # 出口农产品物流
                "chuỗi cung ứng nông sản toàn cầu",  # 全球农产品供应链
                "vận chuyển lạnh cho nông sản",  # 农产品冷链运输
                "bao bì và đóng gói cho xuất khẩu nông sản",  # 出口农产品包装
                "bảo quản sau thu hoạch cho xuất khẩu",  # 出口采后保鲜

                # 价格与市场信息
                "giá nông sản xuất khẩu",  # 出口农产品价格
                "giá FOB nông sản",  # 农产品离岸价
                "giá CIF nông sản",  # 农产品到岸价
                "biến động giá nông sản thế giới",  # 世界农产品价格波动
                "dự báo thị trường nông sản",  # 农产品市场预测
                "báo cáo thị trường nông sản hàng tuần/tháng",  # 农产品市场周报/月报
            ],

            # 相关背景、政策与机构
            context_words=[
                # 机构与组织
                "Bộ Công Thương về nông sản",  # 工贸部（农产品方面）
                "Hiệp hội Xuất khẩu Thủy sản",  # 水产品出口协会
                "Hiệp hội Cà phê Ca cao",  # 咖啡可可协会
                "Hiệp hội Lương thực",  # 粮食协会
                "VINAFRUIT",  # 越南水果协会
                "cơ quan xúc tiến thương mại nông sản",  # 农产品贸易促进机构

                # 政策与战略
                "chiến lược xuất khẩu nông sản",  # 农产品出口战略
                "chính sách hỗ trợ xuất khẩu nông sản",  # 农产品出口支持政策
                "xúc tiến thương mại nông sản",  # 农产品贸易促进
                "hội chợ nông sản quốc tế",  # 国际农产品展会
                "thương hiệu nông sản quốc gia",  # 国家农产品品牌

                # 经济概念
                "cán cân thương mại nông sản",  # 农产品贸易平衡
                "kim ngạch xuất khẩu nông sản",  # 农产品出口额
                "tỷ trọng nông sản trong xuất khẩu",  # 农产品在出口中的比重
                "cung cầu nông sản toàn cầu",  # 全球农产品供需
                "biến động tỷ giá ảnh hưởng đến xuất khẩu nông sản",  # 汇率波动对农产品出口的影响
                "nông sản", "xuất khẩu", "thương mại", "thị trường",
            ],

            # 明确排除的非相关领域
            exclusion_words=[
                # 生产与加工
                "kỹ thuật trồng trọt",  # 种植技术
                "quy trình sản xuất nông nghiệp",  # 农业生产流程
                "chế biến sâu nông sản",  # 农产品深加工
                "công nghệ sau thu hoạch",  # 采后技术（偏生产技术）

                # 非贸易服务
                "dịch vụ kiểm nghiệm nông sản",  # 农产品检测服务（属科技服务）
                "chứng nhận chất lượng nông sản",  # 农产品质量认证（属科技服务）
                "tư vấn kỹ thuật nông nghiệp",  # 农业技术咨询（属科技服务）

                # 其他领域
                "du lịch nông nghiệp",  # 农业旅游
                "phát triển nông thôn tổng thể",  # 综合农村发展
                "chính sách an sinh xã hội nông thôn",  # 农村社会保障政策
            ],

            # 必须包含的核心词根
            required_words=[]
        ),

        # 7. 农业科技服务业
        Domain.TECH_SERVICE: KeywordSet(
            # 核心业务与服务类型 - 最核心、最直接的领域术语
            core_words=[
                "dịch vụ khoa học kỹ thuật nông nghiệp",  # 农业科技服务
                "dịch vụ kỹ thuật nông nghiệp",  # 农业技术服务
                "chuyển giao kỹ thuật nông nghiệp",  # 农业技术转移
                "tư vấn kỹ thuật nông nghiệp",  # 农业技术咨询
                "dịch vụ kiểm nghiệm nông sản",  # 农产品检测服务
                "dịch vụ kiểm định chất lượng nông sản",  # 农产品质量检验服务
                "chứng nhận chất lượng nông sản",  # 农产品质量认证
                "xây dựng tiêu chuẩn nông nghiệp",  # 农业标准制定
                "tiêu chuẩn kỹ thuật nông nghiệp",  # 农业技术标准
                "quy phạm kỹ thuật nông nghiệp",  # 农业技术规范
                "dịch vụ phòng thí nghiệm nông nghiệp",  # 农业实验室服务
                "đào tạo kỹ thuật nông nghiệp",  # 农业技术培训
                "dịch vụ công bố hợp quy nông sản",  # 农产品合规申报服务
                "tư vấn đạt chuẩn nông nghiệp",  # 农业达标咨询
            ],

            # 扩展服务、体系与认证 - 具体的服务项目、认证体系和实践活动
            extension_words=[
                # 检测与认证服务
                "kiểm tra dư lượng thuốc bảo vệ thực vật",  # 农药残留检测
                "phân tích vi sinh vật trong thực phẩm",  # 食品微生物分析
                "kiểm nghiệm chất lượng giống cây trồng",  # 种苗质量检测
                "chứng nhận nông nghiệp hữu cơ",  # 有机农业认证
                "chứng nhận GlobalGAP",  # 全球良好农业规范认证
                "chứng nhận VietGAP",  # 越南良好农业规范认证
                "chứng nhận UTZ",  # UTZ认证（可持续农业）
                "chứng nhận hữu cơ USDA/EU",  # 美国/欧盟有机认证

                # 标准与体系
                "tiêu chuẩn nông nghiệp quốc gia",  # 国家农业标准
                "tiêu chuẩn nông nghiệp quốc tế",  # 国际农业标准
                "hệ thống quản lý chất lượng nông sản",  # 农产品质量管理体系
                "xây dựng quy trình sản xuất nông nghiệp an toàn",  # 安全农业生产规程制定
                "đánh giá rủi ro trong sản xuất nông nghiệp",  # 农业生产风险评估

                # 技术咨询与支持
                "tư vấn ứng dụng công nghệ cao trong nông nghiệp",  # 高科技农业应用咨询
                "đánh giá hiệu quả kỹ thuật nông nghiệp",  # 农业技术效果评估
                "tư vấn lập hồ sơ truy xuất nguồn gốc nông sản",  # 农产品溯源档案咨询
                "hỗ trợ kỹ thuật sau chuyển giao",  # 技术转移后支持
                "dịch vụ hiệu chuẩn thiết bị nông nghiệp",  # 农业设备校准服务

                # 特定领域服务
                "dịch vụ phân tích đất và nước",  # 土壤与水质分析服务
                "chẩn đoán bệnh cây trồng và vật nuôi",  # 动植物疾病诊断
                "đánh giá tác động môi trường nông nghiệp",  # 农业环境影响评估
                "tư vấn xử lý sau thu hoạch",  # 采后处理咨询
                "tư vấn đóng gói và bảo quản nông sản",  # 农产品包装与储藏咨询
                "đánh giá năng suất và chất lượng giống",  # 品种产量与质量评估
            ],

            # 相关背景、政策与概念 - 提供理解该领域的上下文
            context_words=[
                # 政策与法规
                "quy định an toàn thực phẩm",  # 食品安全法规
                "chính sách phát triển khoa học công nghệ nông nghiệp",  # 农业科技发展政策
                "quy chuẩn kỹ thuật quốc gia",  # 国家技术法规
                "luật tiêu chuẩn và quy chuẩn kỹ thuật",  # 标准与技术法规法律
                "quy định về quản lý thuốc bảo vệ thực vật",  # 农药管理法规

                # 机构与体系
                "phòng thí nghiệm được chỉ định",  # 指定实验室
                "tổ chức chứng nhận được công nhận",  # 认可认证机构
                "trung tâm kỹ thuật nông nghiệp",  # 农业技术中心
                "viện nghiên cứu và chuyển giao công nghệ",  # 研究技术转移院
                "chi cục kiểm nghiệm và chất lượng",  # 检验检疫局

                # 相关概念
                "nông nghiệp an toàn",  # 安全农业
                "nông nghiệp bền vững",  # 可持续农业
                "nông sản sạch",  # 清洁农产品
                "truy xuất nguồn gốc",  # 溯源
                "quản lý chất lượng",  # 质量管理
                "đổi mới công nghệ nông nghiệp",  # 农业技术创新
                "logistics sau thu hoạch",  # 采后物流
                "vệ sinh an toàn thực phẩm",  # 食品安全卫生
                "quy trình thực hành nông nghiệp tốt",  # 良好农业规范流程
            ],

            # 明确排除的非相关领域 - 防止领域漂移和误匹配
            exclusion_words=[
                # 生产与贸易 (虽相关，但属于上下游而非服务业本身)
                "sản xuất nông nghiệp trực tiếp",  # 直接农业生产
                "canh tác",  # 耕作
                "thu hoạch",  # 收割
                "chăn nuôi",  # 饲养
                "thương mại nông sản",  # 农产品贸易
                "xuất nhập khẩu nông sản",  # 农产品进出口
                "marketing và bán hàng nông sản",  # 农产品营销与销售

                # 其他领域服务 (易混淆但性质不同的服务)
                "dịch vụ tài chính nông nghiệp",  # 农业金融服务
                "bảo hiểm nông nghiệp",  # 农业保险
                "cho vay vốn nông nghiệp",  # 农业贷款
                "dịch vụ logistics vận tải nông sản",  # 农产品运输物流服务
                "du lịch nông nghiệp",  # 农业旅游

                # 基础和非专业性的教育与推广
                "đào tạo nghề nông nghiệp cơ bản",  # 基础农业职业培训
                "khuyến nông phổ thông",  # 普通农业推广
                "phổ biến kiến thức nông nghiệp đại chúng",  # 大众农业知识普及
            ],

            # 必需词根 - 强制性匹配条件，确保不偏离农业科技服务核心
            required_words=["nông nghiệp", "kỹ thuật", "dịch vụ", "chứng nhận", "tiêu chuẩn", "kiểm nghiệm"]
        ),

        # 8. 休闲农业与乡村旅游业
        Domain.RURAL_TOURISM: KeywordSet(
            # 核心业务模式与业态（第一级核心关键词）
            core_words=[
                "du lịch nông thôn",  # 乡村旅游
                "du lịch nông nghiệp",  # 农业旅游
                "nông nghiệp du lịch",  # 观光农业/休闲农业
                "du lịch sinh thái nông thôn",  # 农村生态旅游
                "du lịch trang trại",  # 农场旅游
                "trải nghiệm nông nghiệp",  # 农业体验
                "tham quan nông trại",  # 农场参观
                "farmstay",  # 农庄住宿（国际通用）
                "homestay nông thôn",  # 农村民宿
                "nhà nghỉ nông thôn",  # 乡村客栈
                "tour nông nghiệp",  # 农业旅游线路
                "tour trải nghiệm nông thôn",  # 乡村体验游
                "du lịch vườn cây ăn trái",  # 果园旅游
                "du lịch làng nghề",  # 手工艺村旅游
                "du lịch cộng đồng nông thôn",  # 农村社区旅游
                "agritourism",  # 农旅（国际术语）
                "du lịch xanh",  # 绿色旅游
                "du lịch nghỉ dưỡng nông thôn",  # 乡村度假
                "du lịch giáo dục nông nghiệp",  # 农业教育旅游
                "du lịch mạo hiểm nông thôn",  # 乡村探险旅游
                "du lịch chữa lành",  # 疗愈旅游（Wellness Tourism）
                "du lịch nông nghiệp công nghệ cao",  # 高科技农业旅游
            ],

            # 扩展体验、产品与服务（二级关键词）
            extension_words=[
                # 具体体验活动
                "thu hoạch nông sản tại vườn",  # 果园采摘
                "tự tay hái trái cây",  # 亲手采摘水果
                "trải nghiệm trồng trọt",  # 种植体验
                "trải nghiệm chăn nuôi",  # 养殖体验
                "câu cá giải trí",  # 休闲垂钓
                "đạp xe tham quan đồng quê",  # 乡村骑行
                "thử làm nông dân một ngày",  # 一日农夫体验
                "trải nghiệm chế biến nông sản",  # 农产品加工体验
                "thăm quan mô hình nông nghiệp",  # 参观农业模式
                "ngắm cảnh đồng quê",  # 观赏田园风光
                "chụp ảnh check-in nông thôn",  # 乡村打卡拍照
                "trải nghiệm đạp xe qua cánh đồng",  # 骑行穿越田野体验

                # 住宿与餐饮
                "lưu trú tại trang trại",  # 农场住宿
                "nhà sàn nông thôn",  # 农村高脚屋
                "biệt thự nông thôn",  # 乡村别墅
                "ẩm thực địa phương",  # 地方美食
                "bữa ăn từ sản phẩm tại vườn",  # 农场直供餐食
                "thưởng thức đặc sản vùng miền",  # 品尝地方特产
                "bữa ăn gia đình nông thôn",  # 农家家常菜
                "tiệc nướng ngoài trời",  # 户外烧烤派对
                "thưởng thức cà phê vườn",  # 花园咖啡体验

                # 节庆、活动与娱乐
                "lễ hội thu hoạch",  # 丰收节
                "lễ hội hoa quả",  # 水果节
                "hội chợ nông sản địa phương",  # 地方农产品集市
                "sự kiện văn hóa nông thôn",  # 农村文化活动
                "biểu diễn nghệ thuật dân gian",  # 民间艺术表演
                "đêm lửa trại",  # 篝火晚会
                "trải nghiệm cưỡi ngựa",  # 骑马体验
                "chèo thuyền tham quan",  # 划船观光
                "ngắm bình minh/hoàng hôn",  # 观赏日出/日落

                # 配套服务与设施
                "hướng dẫn viên địa phương",  # 本地导游
                "dịch vụ cho thuê xe đạp",  # 自行车租赁
                "khu vui chơi nông trại",  # 农场游乐区
                "cửa hàng bán đặc sản địa phương",  # 土特产商店
                "studio chụp ảnh nông thôn",  # 乡村摄影工作室
                "khu cắm trại",  # 露营区
                "hồ bơi tự nhiên",  # 天然泳池
                "spa thảo dược",  # 草药水疗
                "khu tập yoga ngoài trời",  # 户外瑜伽区
                "wifi miễn phí",  # 免费WiFi
            ],

            # 相关背景、理念与政策（三级关联词）
            context_words=[
                # 发展理念与模式
                "du lịch bền vững",  # 可持续旅游
                "du lịch có trách nhiệm",  # 负责任旅游
                "phát triển du lịch cộng đồng",  # 社区旅游发展
                "bảo tồn văn hóa thông qua du lịch",  # 通过旅游保护文化
                "bảo vệ môi trường nông thôn",  # 保护农村环境
                "kinh tế tuần hoàn trong nông nghiệp",  # 农业循环经济
                "du lịch thông minh",  # 智慧旅游
                "du lịch xanh và sạch",  # 绿色清洁旅游

                # 政策、规划与管理
                "quy hoạch du lịch nông thôn",  # 乡村旅游规划
                "chính sách phát triển du lịch địa phương",  # 地方旅游发展政策
                "xây dựng thương hiệu điểm đến",  # 目的地品牌建设
                "hỗ trợ khởi nghiệp du lịch nông thôn",  # 支持乡村旅游创业
                "quản lý điểm du lịch",  # 旅游点管理
                "tiêu chuẩn dịch vụ du lịch nông thôn",  # 乡村旅游服务标准
                "chứng nhận du lịch xanh",  # 绿色旅游认证

                # 市场与营销
                "quảng bá du lịch nông thôn",  # 乡村旅游推广
                "tiếp thị điểm đến",  # 目的地营销
                "kênh bán hàng trực tuyến",  # 线上销售渠道
                "đánh giá và phản hồi của khách hàng",  # 客户评价与反馈
                "mạng xã hội cho du lịch",  # 旅游社交媒体

                # 通用关联词
                "du lịch",  # 旅游
                "giải trí",  # 娱乐
                "nghỉ dưỡng",  # 度假
                "trải nghiệm",  # 体验
                "văn hóa địa phương",  # 地方文化
                "cảnh quan nông thôn",  # 乡村景观
                "điểm đến du lịch",  # 旅游目的地
                "khách du lịch",  # 游客
                "mùa du lịch",  # 旅游旺季
                "lịch trình tham quan",  # 参观行程
            ],

            # 明确排除的非相关领域（精准过滤）
            exclusion_words=[
                # 纯生产与加工领域
                "sản xuất nông nghiệp quy mô lớn",  # 大规模农业生产
                "nhà máy chế biến nông sản",  # 农产品加工厂
                "chuỗi cung ứng nông sản",  # 农产品供应链
                "kho bảo quản nông sản",  # 农产品仓储
                "kỹ thuật canh tác",  # 耕作技术（仅限生产）
                "vật tư nông nghiệp",  # 农业物资

                # 纯贸易与商业活动
                "xuất khẩu nông sản",  # 农产品出口
                "thương mại điện tử nông sản",  # 农产品电商
                "marketing nông sản",  # 农产品营销（非旅游营销）
                "hợp tác xã sản xuất",  # 生产合作社（非旅游合作社）
                "hội chợ thương mại",  # 贸易展会（非旅游节庆）

                # 其他非旅游活动
                "đào tạo nghề nông nghiệp",  # 农业职业培训（除非明确结合旅游）
                "hội thảo khoa học nông nghiệp",  # 农业科学研讨会
                "nghiên cứu phát triển giống cây trồng",  # 作物品种研发
                "chính sách an sinh xã hội nông thôn",  # 农村社会政策（非旅游）
                "xây dựng cơ sở hạ tầng nông thôn",  # 农村基础设施建设（非旅游设施）
                "bảo hiểm nông nghiệp",  # 农业保险
            ],

            # 必须包含的核心词根（组合规则）
            required_words=[
                "du lịch", "nông",  # 必须包含“旅游”和“农”相关词根
                "trải nghiệm",   # 或“体验”
                "tham quan",  # 或“参观”
                "nghỉ dưỡng", "nông thôn"  # “度假”和“农村”
            ]
        ),

        # 9. 农业文化
        Domain.AGRICULTURE_CULTURE: KeywordSet(
            # 核心概念 - 农业文化遗产的核心要素
            core_words=[
                "văn hóa nông nghiệp",  # 农业文化
                "văn hóa truyền thống nông nghiệp",  # 传统农业文化
                "di sản văn hóa nông nghiệp",  # 农业文化遗产
                "di sản nông nghiệp quan trọng",  # 重要农业遗产
                "phong tục nông nghiệp",  # 农业习俗
                "lễ hội nông nghiệp",  # 农业节庆
                "lễ hội mùa vụ",  # 季节节庆
                "nghề truyền thống nông thôn",  # 农村传统职业
                "thủ công mỹ nghệ nông thôn",  # 农村手工艺
                "văn hóa làng nghề",  # 手工艺村文化
                "kiến trúc nông thôn truyền thống",  # 传统农村建筑
            ],

            # 扩展概念 - 具体表现形式、实践与保护
            extension_words=[
                # 农业知识体系
                "tri thức bản địa nông nghiệp",  # 农业本土知识
                "kinh nghiệm canh tác truyền thống",  # 传统耕作经验
                "bí quyết nghề nông",  # 农业秘诀
                "tín ngưỡng nông nghiệp",  # 农业信仰
                "tập quán canh tác",  # 耕作习俗

                # 具体文化实践
                "lễ hội cầu mùa",  # 祈丰收节
                "lễ hội xuống đồng",  # 下田节
                "lễ tạ ơn đất",  # 谢土节
                "hội làng truyền thống",  # 传统村会
                "trò chơi dân gian nông thôn",  # 农村民间游戏
                "ẩm thực nông thôn truyền thống",  # 传统农村美食
                "dân ca, dân vũ nông nghiệp",  # 农业民歌民舞
                "nghệ thuật dân gian nông thôn",  # 农村民间艺术

                # 保护与传承
                "bảo tồn di sản nông nghiệp",  # 农业遗产保护
                "phục hồi làng nghề",  # 手工艺村复兴
                "truyền dạy nghề truyền thống",  # 传统职业传承
                "nghệ nhân nông nghiệp",  # 农业艺人
                "nghệ nhân làng nghề",  # 手工艺村艺人
                "sưu tầm văn hóa nông nghiệp",  # 农业文化收集
                "ghi chép di sản nông nghiệp",  # 农业遗产记录
                "khu bảo tồn văn hóa nông nghiệp",  # 农业文化保护区
            ],

            # 上下文关联 - 相关领域与背景
            context_words=[
                # 地域与社区
                "làng xã truyền thống",  # 传统乡村
                "cộng đồng nông thôn",  # 农村社区
                "địa phương",  # 地方
                "vùng miền",  # 地区

                # 文化遗产体系
                "di sản văn hóa phi vật thể",  # 非物质文化遗产
                "di sản văn hóa vật thể",  # 物质文化遗产
                "di sản thế giới nông nghiệp",  # 世界农业遗产
                "di sản văn hóa UNESCO",  # UNESCO文化遗产

                # 发展与政策
                "phát triển văn hóa nông thôn",  # 农村文化发展
                "du lịch văn hóa nông nghiệp",  # 农业文化旅游
                "bảo tồn và phát huy giá trị văn hóa",  # 文化价值保护与发扬
                "chính sách bảo tồn di sản",  # 遗产保护政策
                "quy hoạch bảo tồn làng nghề",  # 手工艺村保护规划
            ],

            # 排除领域 - 明确边界
            exclusion_words=[
                "kỹ thuật canh tác",  # 耕作技术（偏生产技术）
                "sản xuất nông nghiệp hiện đại",  # 现代农业生产
                "công nghệ nông nghiệp",  # 农业技术
                "thương mại nông sản",  # 农产品贸易
                "marketing nông sản",  # 农产品营销
                "quản lý trang trại",  # 农场管理
                "đào tạo nghề nông nghiệp",  # 农业职业培训（虽然相关但属教育领域）
                "nghiên cứu khoa học nông nghiệp",  # 农业科学研究
            ],

            # 必需词根 - 确保主题不偏离
            required_words=["văn hóa", "nông", "truyền thống"]
        ),

        # 10. 农业职业教育
        Domain.VOCATIONAL_EDU: KeywordSet(
            # 核心业务概念 - 最直接的领域术语
            core_words=[
                "đào tạo nghề nông nghiệp",  # 农业职业培训
                "giáo dục nghề nghiệp nông nghiệp",  # 农业职业教育
                "đào tạo nông dân",  # 农民培训
                "dạy nghề nông nghiệp",  # 农业技能教学
                "trường dạy nghề nông nghiệp",  # 农业职业学校
                "trung tâm đào tạo nông nghiệp",  # 农业培训中心
                "khóa học nông nghiệp",  # 农业课程
                "chương trình đào tạo nông nghiệp",  # 农业培训项目
                "phát triển nguồn nhân lực nông nghiệp",  # 农业人力资源开发
                "nâng cao tay nghề nông dân",  # 提升农民技能

                "giáo dục nghề nghiệp",  # 职业教育（文本中直接出现）
                "tuyển sinh giáo dục nghề nghiệp",  # 职业教育招生
                "đào tạo nghề cho lao động nông thôn",  # 农村劳动力职业培训
                "lớp đào tạo nghề",  # 职业培训班
                "chỉ tiêu đào tạo nghề",  # 职业培训指标
                "giáo dục nghề nghiệp",  # 职业教育（文本核心词）
                "tuyển sinh giáo dục nghề nghiệp",  # 职业教育招生
                "đào tạo nghề cho lao động nông thôn",  # 农村劳动力职业培训
                "lớp đào tạo nghề",  # 职业培训班
                "chỉ tiêu đào tạo nghề",  # 职业培训指标
                "kế hoạch đào tạo nghề",  # 职业培训计划
                "lao động nông thôn học nghề",  # 农村劳动力学技能
                "đào tạo nghề tại nông thôn",  # 农村地区职业培训
            ],

            # 扩展领域 - 具体培训形式、内容与技术
            extension_words=[
                # 培训类型
                "đào tạo nghề ngắn hạn",  # 短期职业培训
                "đào tạo tại chỗ",  # 现场培训
                "đào tạo từ xa nông nghiệp",  # 远程农业培训
                "đào tạo liên kết",  # 合作培训
                "đào tạo theo hợp đồng",  # 合同制培训
                "đào tạo chuyên sâu",  # 深度培训

                # 证书与资质
                "chứng chỉ nghề nông nghiệp",  # 农业职业证书
                "văn bằng nghề nông nghiệp",  # 农业职业文凭
                "chứng nhận kỹ năng nghề",  # 职业技能认证
                "đánh giá kỹ năng nghề",  # 职业技能评估

                # 具体技术领域（农业细分）
                "đào tạo kỹ thuật trồng trọt",  # 种植技术培训
                "đào tạo chăn nuôi",  # 畜牧养殖培训
                "đào tạo thủy sản",  # 水产养殖培训
                "đào tạo lâm nghiệp",  # 林业培训
                "đào tạo nông nghiệp công nghệ cao",  # 高科技农业培训
                "đào tạo nông nghiệp hữu cơ",  # 有机农业培训
                "đào tạo bảo vệ thực vật",  # 植物保护培训
                "đào tạo quản lý trang trại",  # 农场管理培训
                "đào tạo chế biến nông sản",  # 农产品加工培训
                "đào tạo nông nghiệp thông minh",  # 智慧农业培训
                "đào tạo sử dụng thiết bị nông nghiệp",  # 农业设备使用培训
            ],

            # 上下文与关联领域 - 政策、教育、发展等
            context_words=[
                # 教育相关
                "giáo dục",  # 教育
                "đào tạo",  # 培训
                "kỹ năng",  # 技能
                "thực hành",  # 实践
                "giáo trình nông nghiệp",  # 农业教材
                "giáo viên dạy nghề nông nghiệp",  # 农业职业教师
                "học viên nông nghiệp",  # 农业学员

                # 政策与项目
                "chính sách đào tạo nghề nông thôn",  # 农村职业培训政策
                "dự án phát triển nông thôn",  # 农村发展项目
                "xây dựng nông thôn mới",  # 新农村建设
                "chuyển đổi số nông nghiệp",  # 农业数字化转型
                "tái cơ cấu nông nghiệp",  # 农业结构调整

                # 发展相关
                "phát triển nông thôn",  # 农村发展
                "xóa đói giảm nghèo",  # 扶贫减贫
                "tăng thu nhập nông dân",  # 增加农民收入
                "phát triển bền vững nông nghiệp",  # 农业可持续发展
                "khởi nghiệp nông nghiệp",  # 农业创业

                # 文本中涉及的机构和政策背景
                "Sở Lao động - Thương binh và Xã hội",  # 劳动荣军与社会厅
                "cơ sở đào tạo tại các huyện",  # 县级培训机构
                "địa bàn nông thôn",  # 农村地区
                "tuyên truyền tuyển sinh",  # 招生宣传
                "đơn vị liên quan",  # 相关单位
                "kế hoạch năm",  # 年度计划
                "đánh giá chung của ngành",  # 行业总体评估

                # 政府部分与机构
                "Sở Lao động - Thương binh và Xã hội",  # 劳动荣军与社会厅
                "ngành chức năng",  # 职能部门
                "cơ quan quản lý đào tạo nghề",  # 职业培训管理机构

                # 时间与计划
                "tính đến hết tháng",  # 截至月底
                "tháng cuối năm",  # 年底月份
                "đẩy mạnh đào tạo cuối năm",  # 年底加强培训
                "kế hoạch năm 2019",  # 2019年计划

                # 评估与问题
                "đánh giá chung của ngành",  # 行业总体评估
                "tiến độ đạt thấp",  # 进度偏低
                "nguyên nhân hạn chế",  # 限制原因
                "vấn đề trong tổ chức đào tạo",  # 培训组织中的问题

                # 解决方案与措施
                "tích cực tuyên truyền tuyển sinh",  # 积极宣传招生
                "đẩy mạnh đào tạo nghề",  # 加强职业培训
                "phối hợp đơn vị liên quan",  # 配合相关单位
                "tổ chức tuyển sinh tập trung",  # 集中组织招生
            ],

            # 排除领域 - 明确区分相近但不属于的领域
            exclusion_words=[
                "sản xuất nông nghiệp",  # 农业生产（虽然相关，但更偏生产而非教育）
                "thương mại nông sản",  # 农产品贸易
                "du lịch nông thôn",  # 乡村旅游
                "công nghiệp chế biến",  # 加工工业
                "nghiên cứu khoa học nông nghiệp",  # 农业科学研究（偏学术研究）
                "thị trường lao động chung",  # 普通劳动力市场
                "đào tạo đại học nông nghiệp",  # 大学农业教育（偏高等教育）
                "phát triển công nghệ nông nghiệp",  # 农业技术研发
                # 文本中出现的具体培训类型和问题
                "đào tạo nghề cho LĐNT",  # 农村劳动力培训（LĐNT = lao động nông thôn）
                "mở lớp đào tạo nghề",  # 开设职业培训班
                "cơ sở đào tạo",  # 培训机构
                "khó khăn trong tổ chức mở lớp",  # 开班困难
                "nguồn lao động trong độ tuổi",  # 适龄劳动力资源
                "tiến độ thực hiện chỉ tiêu",  # 指标实施进度

                "tiến độ đào tạo nghề",  # 职业培训进度
                "thực hiện chỉ tiêu đào tạo",  # 执行培训指标
                "tổ chức mở lớp đào tạo",  # 组织开办培训班
                "khó khăn trong mở lớp",  # 开班困难
                "đạt tỷ lệ đào tạo",  # 达成培训比例

                # 招生与资源
                "nguồn lao động trong độ tuổi",  # 适龄劳动力资源
                "tuyển sinh học nghề",  # 招生学技能
                "thiếu lao động học nghề",  # 缺乏学技能的劳动力
                "địa bàn có ít lao động",  # 劳动力少的地区

                # 机构与单位
                "cơ sở đào tạo tại huyện",  # 县级培训机构
                "đơn vị liên quan giáo dục nghề",  # 相关职业教育单位
                "trung tâm dạy nghề huyện",  # 县级职业技能中心

            ],

            # 必需词根 - 确保不偏离主题
            required_words=["nông nghiệp", "đào tạo", "nghề","nông thôn", "lao động", "đào tạo", "nghề"],
        )
    }
