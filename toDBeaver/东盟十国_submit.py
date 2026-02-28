from utils.db_operations import DatabaseOperations
import pandas as pd
from datetime import datetime
import os

class DBeaverOperations(DatabaseOperations):
    def __init__(self, folderpath=None):
        super().__init__()
        self.folderpath = folderpath

    def _insert(self, md5):
        """插入数据"""
        try:
            file_path = os.path.join(self.folderpath, r"seen.csv")
            df = pd.read_csv(file_path)
            start_index = 0
            insert_count = read_count = start_index
            data_slice = df.values[start_index:]
            for item in data_slice:
                try:
                    lan = item[0]
                    labels = item[1]
                    md5 = item[2]
                    url = item[3]
                    file_type = item[4]
                    file_name = item[5]

                    # 数据库中存在已经插入的数据即跳过
                    if md5 in names:
                        read_count += 1
                        continue
                    read_count += 1
                    user = '李馨彤'  # 采集人
                    submit_time = datetime.now()

                    sql = """ 
                                INSERT INTO `东盟十国特定领域文本采集` VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                            """
                    value = (submit_time, user, lan, labels, md5, url, file_type, file_name)
                    success = self.insert_data(sql, value)

                    if success:
                        insert_count += 1
                    else:
                        print(insert_count)

                    # 可选：批量提交以提高性能
                    if insert_count % 100 == 0:
                        print(f"已处理 {insert_count} 条数据")

                except Exception as e:
                    print(f"处理单条数据失败: {e}")
                    break

            print(f"总共处理了 {insert_count} 条数据")
            return True
        except Exception as e:
            print(f"流式处理JSON文件失败: {e}")
            return False
    def _get(self):
        """从数据库中获取数据"""
        exists_path = os.path.join(self.folderpath,'exists_seen.csv')

        SQL = "SELECT * FROM `东盟十国特定领域文本采集`"
        results = self.search_data(SQL)
        names = [row[4] for row in results]

        # pd.DataFrame(names).to_csv(exists_path, index=False,header=False,encoding="utf-8-sig")
        return names

# 使用示例
if __name__ == "__main__":
    path = r"D:\DATA\DATA\东盟十国特定领域文本采集\submit-越南语\种植业"
    deal_file = DBeaverOperations(path)
    try:
        deal_file.connect()
        #
        # # 1.从数据库或者CSV中提取数据
        # names = deal_file._get()
        # print(f'共有{len(names)}条数据')
        # # md5 = pd.read_csv(os.path.join(path,'exists_seen.csv'),header=None).iloc[:,0].to_list()
        names = []
        # 2. 插入数据
        deal_file._insert(names)
    except Exception as e:
        print(f"处理数据失败: {e}")
    finally:
        deal_file.close()
