"""
文本数据转CSV
"""
from utils.to_csv import TEXTToCSV
path = r"D:\DATA\DATA\英日西阿特定领域采集\英语"
tc = TEXTToCSV()
# 已去重 —— 根据URL链接 + 标题和链接的md5值
tc.to_csv(path)


"""
图片数据转CSV
# """
# from utils.to_csv import PictureToCSV
# pc = PictureToCSV()
# picture_folder = r'D:\DATA\pictures\流程图2\流程图'
# csv_path = r'D:\DATA\Pictures\seen.csv'
# pc.to_csv(picture_folder,csv_path,mode='a')


"""
剧本杀文件夹转CSV
"""
# from utils.to_csv import MurderToCSV
# path = r"D:\BaiduNetdiskDownload\剧本杀\剧本杀"
# pan = MurderToCSV(path)
# pan.normalize_filename()
# pan.tocsv()

"""
CSV通用
"""
# from utils.to_csv import ConfigCSV
# cc = ConfigCSV()
# ## 获取数据长度 - json pdf jpg png
# cc.len_data(r"D:\样例")
## csv 文件去重
# cc.duplicate(r"d://seen.csv")