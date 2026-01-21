import pandas as pd
import re
import os
# 2026-01-05 13:54:58,348 - INFO - __main__ -从https://www.processon.com/template/flow/at_page2890提取到60个目标URL

__all__ =  ['ProcessLog']
class ProcessLog:
    def __init__(self):
        df = pd.read_csv('num.txt',header=None)
        self.alread_num = df.iloc[:,0].to_list()

    def get_num(self):
        log_path = r"/.A-Pictures_Crawler/pictures_log.log"
        df = pd.read_csv(log_path, header=None)

        log_info = df.iloc[:, 1].to_list()

        log_list = []
        for i in log_info:
            if '提取到60个目标URL' in i:
                pattern = r"https://www.processon.com/template/flow/at_page(.*?)提取到"
                num = re.findall(pattern, i)
                if not len(num):
                    continue
                log_list.append(int(num[0]))

        os.remove(log_path)
        no_num = []  # 2385
        for i in log_list:
            if i in self.alread_num:
                self.alread_num.remove(i)
        print(len(log_list))
        print(len(self.alread_num))
        print(self.alread_num)
        df = pd.DataFrame(self.alread_num)
        df.to_csv('num.txt', index=False, header=False)
        return self.alread_num
