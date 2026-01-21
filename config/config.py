# config.py - 系统配置文件
"""
东盟国家语言配置
"""
ASEAN_LANGUAGES = {
    '缅甸语': {
        'code': 'my',  # ISO 639-1代码
        'script': 'မြန်မာအက္ခရာ',  # 缅甸文
        'keywords': ['စိုက်ပျိုးရေး', 'ငါးဖမ်းခြင်း'],  # 种植业、渔业
        'stopwords': ['ဖြစ်သည်', 'များ']  # 停用词
    },
    '高棉语': {
        'code': 'km',
        'script': 'អក្សរខ្មែរ',
        'keywords': ['កសិកម្ម', 'នេសាទ'],
        'stopwords': ['គឺ', 'និង']
    },
    '泰语': {
        'code': 'th',
        'script': 'ภาษาไทย',
        'keywords': ['การเกษตร', 'การประมง'],
        'stopwords': ['คือ', 'และ']
    },
    '越南语': {
        'code': 'vi',
        'script': 'Tiếng Việt',
        'keywords': ['nông nghiệp', 'ngư nghiệp'],
        'stopwords': ['là', 'và']
    }
}

# 网站分类配置
WEBSITE_CATEGORIES = {
    '种植业': {
        'keywords': ['agriculture', 'farming', 'crops', '种植', '农业'],
        'priority': 1
    },
    '渔业': {
        'keywords': ['fishery', 'aquaculture', 'fishing', '渔业', '水产'],
        'priority': 2
    },
    '农产品贸易': {
        'keywords': ['trade', 'export', 'import', '贸易', '出口'],
        'priority': 3
    }
}

# 目标网站列表（按国家分类）
TARGET_WEBSITES = {
    '缅甸语': [
        {
            'name': '缅甸农业部',
            'url': 'https://www.myanmaragriculture.gov.mm',
            'category': '种植业',
            'check_interval': 3600,  # 1小时
            'selectors': {
                'article': 'div.article-content',
                'title': 'h1.entry-title',
                'date': 'span.post-date',
                'content': 'div.post-body'
            }
        },
        {
            'name': '缅甸渔业局',
            'url': 'https://fisheries.gov.mm',
            'category': '渔业',
            'check_interval': 1800
        }
    ],
    '高棉语': [
        {
            'name': '柬埔寨农业局',
            'url': 'https://www.maff.gov.kh',
            'category': '种植业',
            'check_interval': 7200
        }
    ]
}