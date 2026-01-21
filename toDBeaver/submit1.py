from utils.db_operations import DatabaseOperations
from utils.file_io import DealFile
import os
import pandas as pd
from datetime import datetime


class Read_To_Insert(DealFile):
    def __init__(self, folderpath=None):
        super().__init__()
        self.folderpath = folderpath

    def Extract_data(self, db_ops):
        """取数据"""
        # 连接数据库
        if not db_ops.connect():
            print("数据库连接失败，无法继续执行")
            return

        # ------------------------------------------------------------------------
        filename = r"seen.csv"
        file_path = self.folderpath
        file_path = os.path.join(file_path, filename)

        try:
            df = pd.read_csv(file_path)
            count = 347879
            read_count = 0
            for item in df.values:
                try:
                    # 处理单个数据项并写入数据库
                    lan = item[0]
                    labels = item[1]
                    md5 = item[2]
                    url = item[3]
                    file_type = item[4]
                    file_name = item[5]

                    read_count += 1
                    # 写入数据库
                    if read_count < 347879 or read_count > 537976:  # and read_count <  227879  -  537976
                        print(read_count)
                        continue

                    success = self.insert_data(db_ops, lan, labels, md5, url, file_type, file_name)
                    if success:
                        count += 1
                    else:
                        print(count)

                    # 可选：批量提交以提高性能
                    if count % 100 == 0:
                        print(f"已处理 {count} 条数据")

                except Exception as e:
                    print(f"处理单条数据失败: {e}")
                    break
            self.stop_database(db_ops)
            print(f"总共处理了 {count} 条数据")
            return True
        except Exception as e:
            print(f"流式处理JSON文件失败: {e}")
            return False

    def create_data(self):
        # 创建数据库操作实例
        db_ops = DatabaseOperations()
        return db_ops

    def stop_database(self, db_ops):
        # 关闭连接
        db_ops.close()

    def insert_data(self, db_ops, lan, labels, md5, url, file_type, file_name):
        """
        采集时间、采集人、语种、领域、UUID（和JSON中对应id一致）、URL、字符数量
        """
        # 定义方言文本采集所需的字段数据
        user = '李馨彤'  # 采集人
        submit_time = datetime.now()
        try:
            # 检查数据库连接状态
            if not db_ops.conn or not db_ops.cursor:
                print("数据库连接已断开，尝试重新连接...")
                if not db_ops.connect():
                    print(f"重新连接数据库失败 ID {id}")
                    return False
            sql = """ 
                INSERT INTO `东盟十国特定领域文本采集` VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            value = (submit_time, user, lan, labels, md5, url, file_type, file_name)
            success = db_ops.insert_script_data(sql, value)
            return success
        except Exception as e:
            print(f"插入数据失败 ID {id}: {e}")
            return False


# 使用示例
if __name__ == "__main__":
    # 提取 "文件名+链接"
    path = r"D:\DATA\DATA\12月份-东盟十国语料采集4\越南语"
    deal_file = Read_To_Insert(path)
    db_ops = deal_file.create_data()
    deal_file.Extract_data(db_ops)
