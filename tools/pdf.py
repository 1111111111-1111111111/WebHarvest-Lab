import requests
import hashlib
import os
import logging
import urllib3
from tools.classificate_domain import AgricultureClassifier
from bs4 import BeautifulSoup
from config.headers import HEADERS
from docx import Document
from io import BytesIO
import pandas as pd
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
agri = AgricultureClassifier()
logger = logging.getLogger(__name__)

dic = {"越南语":"vi","印尼语":"id","马来语":"ms","西班牙语":"es","泰语":"th",
                    "缅甸语":"my","高棉语":"km","老挝语":"lo","菲律宾语":"tl" }
dic_1 = {'英语':'en','阿拉伯语':'ar','西班牙语':'es','日语':'ja'}
class PdfDownloader:
    def __init__(self,path):
        self.path = path


    def download_pdf(self, url,args=None):
        """下载PDF文件"""
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                if url.endswith(('.doc','.docx')):
                    doc_stream = BytesIO(resp.content)
                    doc = Document(doc_stream)
                    text_content =[p.text for p in doc.paragraphs]
                    full_text =  ' '.join(text_content)

                    result = agri.classify(full_text,"")
                    path = os.path.join(self.path, result.domain_name)
                    if not os.path.exists(path):
                        os.makedirs(path)

                # 计算PDF二进制内容的MD5
                content_md5 = hashlib.md5(resp.content).hexdigest()
                ext = url.split('.')[-1].split('?')[0]
                filename = f"{content_md5}.{ext}"

                fina_path = os.path.join(self.path, filename)
                with open(fina_path, "wb") as f:
                    f.write(resp.content)
                ind = self.path.split('\\')[-3]
                labels = self.path.split('\\')[-2]
                file_type = self.path.split('\\')[-1]
                res = {
                    "lan": dic_1[ind],
                    "labels": labels,
                    "md5": content_md5,
                    "url": url,
                    "file_type": file_type,
                    "filename": content_md5
                }
                df = pd.DataFrame([res])
                df.to_csv(os.path.join(self.path, "seen_pdf.csv"), mode='a', header=False, index=False,encoding='utf-8-sig')
                print(f"【INFO】 ✓ {ext}已保存: {filename} -> {fina_path}")
                return True
            else:
                print(f"【ERROR】 ✗ 下载失败，状态码: {resp.status_code}")
                return False

        except Exception as e:
            print(f"【ERROR】 ✗ 发生错误: {e}")
if __name__ == '__main__':
    pdf = PdfDownloader(r"D:\DATA\DATA\英日西阿特定领域采集\英语\医疗\pdf")
    # url = r"https://thuybk@moit.gov.vn/upload/2005517/20251008/Du_thao_Nghi_dinh_qd_ve_ung_dung_KHCN_va_phat_trien_CN_che_tao_trong_lv_dien_luc_52981_b8ce2.docx"
    pdf.download_pdf(url=r"https://www.cdc.gov/lyme/media/pdfs/Lyme-disease-prevention-fact-sheet-tagalog.pdf")



