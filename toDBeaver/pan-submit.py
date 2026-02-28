from utils.db_operations import DatabaseOperations
import os
import pandas as pd
from datetime import datetime
import shutil

class DBeaverOperations(DatabaseOperations):
    def __init__(self, folderpath=None):
        super().__init__()
        self.folderpath = folderpath

    def _insert(self,names):
        """插入数据"""
        try:
            file_path = os.path.join(self.folderpath, r"seen.csv")
            df = pd.read_csv(file_path)
            start_index = 0
            insert_count = read_count  = start_index
            data_slice = df.values[start_index:]
            for item in data_slice:
                try:
                    pan_type = item[0]
                    pan_name = item[1]

                    # 数据库中存在已经插入的数据即跳过
                    if pan_name in names:
                        read_count +=1
                        continue
                    read_count += 1

                    user = '李馨彤'  # 采集人
                    submit_time = datetime.now()
                    sql = "INSERT INTO `剧本杀文本采集` VALUES (%s,%s,%s,%s)"
                    value = (submit_time, user, pan_type, pan_name)
                    success = self.insert_data(sql, value)
                    if success:
                        insert_count += 1
                    else:
                        print(insert_count)

                    if insert_count % 100 == 0:
                        print(f"已处理 {insert_count} 条数据")
                except Exception as e:
                    print(f"处理单条数据失败: {e}")
                    break
            print(f"总共处理了 {read_count} 条数据")
            return True

        except Exception as e:
            print(f"插入数据失败 ID {id}: {e}")
            return False

    def _get(self):
        """从数据库中获取数据"""
        exists_path = os.path.join(self.folderpath,'exists_seen.csv')

        SQL = "SELECT * FROM `剧本杀文本采集`"
        results = self.search_data(SQL)
        names = [row[3] for row in results]

        pd.DataFrame(names).to_csv(exists_path, index=False,header=False,encoding="utf-8-sig")
        return names

# 使用示例
if __name__ == "__main__":
    path = r"D:\BaiduNetdiskDownload\剧本杀\剧本杀"

    deal_file = DBeaverOperations(path)

    try:
        deal_file.connect()

        # 1.从数据库或者CSV中提取数据
        # names = deal_file._get()
        # md5 = pd.read_csv(os.path.join(path,'exists_seen.csv'),header=None).iloc[:,0].to_list()

        # 2. 插入数据
        deal_file._delete()
    except Exception as e:
        print(f"处理数据失败: {e}")
    finally:
        deal_file.close()
