from utils.db_operations import DatabaseOperations
import pandas as pd
from datetime import datetime
import os
import shutil

class DBeaverOperations(DatabaseOperations):
    def __init__(self,path):
        super().__init__()
        self.folderpath = path

    def _insert(self, data):
        """从CSV文件中取数据"""
        try:
            inseart_path = os.path.join(self.folderpath,'seen.csv')
            df = pd.read_csv(inseart_path)
            start_index = 0
            inseart_count = start_index
            read_count = start_index
            dup_count = 0
            data_slice = df.values[start_index:]
            for item in data_slice:
                try:
                    con = item[0]
                    image_format = item[1]
                    type = item[2]
                    if con in data:
                        print(f'数据已存在，已跳过！')
                        dup_count += 1
                        path = r"D:\DATA\pictures\流程图-数据库"
                        init_path = os.path.join(r"D:\DATA\pictures",f'{type}',f'{con}.{image_format}')
                        if not os.path.exists(init_path):
                            continue
                        else:
                            shutil.move(init_path,path)
                            os.remove(init_path)
                            continue
                    image_info = type

                    read_count += 1
                    # 写入数据库
                    value = [con,image_format,image_info]
                    name = '李馨彤'
                    submit_time = datetime.now()

                    Value = (submit_time, name, value[0], value[1], value[2])
                    # (`采集时间` `采集人` `MD5` `图片格式` `流程图类型`)
                    SQL = "INSERT INTO `流程图采集表` VALUES (%s,%s,%s,%s,%s)"
                    success = self.insert_data(SQL, Value)
                    if success:
                        inseart_count += 1
                    else:
                        print(inseart_count)

                    if inseart_count % 100 == 0:
                        print(f"已处理 {inseart_count} 条数据")

                except Exception as e:
                    print(f"处理单条数据失败: {e}")
                    continue
            print(f"已提交 {read_count} 条数据")
            print(f"重复数据 {dup_count} 条数据")

            return True
        except Exception as e:
            print(f"流式处理JSON文件失败: {e}")
            return False

    def _get(self):
        """从数据库中获取数据"""
        exists_path = os.path.join(self.folderpath,'exists_seen.csv')

        SQL = "SELECT * FROM `流程图采集表`"
        results = self.search_data(SQL)
        md5 = [row[2] for row in results]
        pd.DataFrame(md5).to_parquet('data.parquet', compression='snappy')
        return md5

    def _delete(self):
        """删除数据"""
        file_path = os.path.join(self.folderpath, r"seen.csv")

        df = pd.read_csv(file_path, header=None)
        count = 0
        for md5 in df.iloc[:, 0][3500:]:
            SQL = "DELETE FROM `流程图采集表` WHERE `MD5` = %s AND `采集人` = %s"
            values = (md5, '李馨彤')
            res = self.delete_data(SQL,values)
            if res:
                print(f'删除{md5}值成功')
            else:
                print(f'删除{md5}值失败')


# 使用示例
if __name__ == "__main__":
    # 提取 "文件名+链接"
    path = r"D:\DATA\pictures"
    deal_file = DBeaverOperations(path)
    try:
        db_ops = deal_file.connect()

        # 1.从数据库或者CSV中提取数据
        # md5 = deal_file._get()
        # md5 = pd.read_parquet('data.parquet').iloc[:, 0].to_list()
        # print(f'数据库中已存在 {len(md5)} 条数据')

        # 2. 插入数据
        deal_file._delete()
    except Exception as e:
        print(f"处理数据失败: {e}")
    finally:
        deal_file.close()