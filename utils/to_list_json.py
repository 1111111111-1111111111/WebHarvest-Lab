from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.file_io import DealFile
import os
import glob
import shutil
from datetime import datetime
from tools.classificate_domain import AgricultureClassifier
import fasttext
import multiprocessing

class DictToArray:
    def __init__(self):
        self.dealfile = DealFile()

    @staticmethod
    def _load_model_once():
        """每个进程加载一次模型的静态方法"""
        model_path = r'D:\Scrapy\models\lid\lid.176.ftz'
        return fasttext.load_model(model_path)

    def _process_file(self, file_info, now_time, output_path, target_folder, model):
        """处理单个文件的函数，用于并行执行"""
        file, type_classification = file_info
        time = os.path.getmtime(file)
        modified_date = datetime.fromtimestamp(time)

        # 修复：正确地解析时间字符串
        compare_time = datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')

        if modified_date < compare_time:
            filename = os.path.basename(file)
            dir_path = os.path.dirname(file)

            try:
                content = self.dealfile.read_json(filename, dir_path)

                if content["title"] is None or content["content"] is None:
                    # 异步写入文件，避免频繁IO
                    with multiprocessing.Lock():  # 创建临时锁
                        os.makedirs(output_path, exist_ok=True)
                        self.dealfile.write_txt(f"no_title.txt", output_path, content["url"] + '\n', "a")
                    return {"action": "delete", "file": file, "content": None}

                # 分类
                # classifier = AgricultureClassifier()
                # classifier_result = classifier.classify(content["title"], content["content"])
                # if classifier_result.domain_name != type_classification:
                #     others_folder = os.path.join(os.path.dirname(dir_path), classifier_result.domain_name)
                #     return {"action": "move", "file": file, "dest": others_folder}

                con = content["title"] + content["content"]
                clean_con = "".join(con.split())

                # 验证语言
                predictions = model.predict(clean_con)
                label = predictions[0][0].replace('__label__', '')

                if label != content["language"]:
                    others_folder = fr"{os.path.dirname(dir_path)}/{label}"
                    os.makedirs(others_folder, exist_ok=True)
                    return {"action": "move_lang", "file": file, "dest": others_folder}

                return {"action": "keep", "file": file, "content": content, "url": content["url"]}

            except Exception as e:
                print(f"处理文件 {file} 时出错: {e}")
                return {"action": "error", "file": file, "error": str(e)}

        return {"action": "skip", "file": file}

    def merge_json_files_by_url(self, id, output_path, target_folder, path1, path2=None, path3=None, path4=None,
                                path5=None,labels=None):
        """合并两个文件夹下的JSON文件，按URL去重"""
        path_list = [path for path in [path1, path2, path3, path4, path5] if path]
        delete_count = 0
        save_count = 0
        dupli_count = 0
        url_to_content = {}
        now_time = input("请输入需要读取文件的截止日期：")

        try:
            # while True:
            # 收集所有需要处理的文件
            all_files = []
            for path in path_list:
                os.makedirs(path, exist_ok=True)
                type_classification = os.path.basename(path)
                files = glob.glob(f"{path}/*.json")
                for file in files:
                    all_files.append((file, type_classification))

            print(f"找到 {len(all_files)} 个文件需要处理...")
            try:
                batch_size = 10000  # 每批处理10000个文件
                for i in range(0, 100000, batch_size):
                    batch = all_files[i:i + batch_size]
                    print(
                        f"处理批次 {i // batch_size + 1}/{(len(all_files) - 1) // batch_size + 1}，包含 {len(batch)} 个文件...")

                    # 使用进程池处理文件，每个进程加载一次模型
                    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                        # 为每个任务准备参数
                        tasks = []
                        for file_info in batch:
                            tasks.append((file_info, now_time, output_path, target_folder))

                        # 使用starmap并行处理
                        results = pool.starmap(self._process_file_wrapper, tasks)

                        for result in results:
                            try:
                                if result["action"] == "delete":
                                    delete_count += 1
                                    if os.path.exists(result["file"]):
                                        os.remove(result["file"])
                                        print(f'已经删除无内容标题文件：{result["file"]}')

                                elif result["action"] == "move":
                                    if not os.path.exists(result["dest"]):
                                        os.makedirs(result["dest"], exist_ok=True)
                                    if os.path.exists(result["file"]):
                                        shutil.move(result["file"], result["dest"])
                                        print(f"{os.path.basename(result['file'])} -> {os.path.basename(result['dest'])}")

                                elif result["action"] == "move_lang":
                                    if os.path.exists(result["file"]):
                                        shutil.move(result["file"], result["dest"])
                                        print(f"{os.path.basename(result['file'])} -> {os.path.basename(result['dest'])}")

                                elif result["action"] == "keep":
                                    if result["url"] not in url_to_content:
                                        save_count += 1
                                        url_to_content[result["url"]] = result["content"]
                                        if not os.path.exists(target_folder):
                                            os.makedirs(target_folder, exist_ok=True)
                                        if os.path.exists(result["file"]):
                                            shutil.move(result["file"], target_folder)
                                            print(f"{os.path.basename(result['file'])} -> {os.path.basename(target_folder)}")
                                    else:
                                        if os.path.exists(result["file"]):
                                            os.remove(result["file"])
                                            print(f'已经删除重复文件：{result["file"]}')
                                            dupli_count += 1

                            except Exception as e:
                                print(f"处理结果时出错: {e}")

                    print(f"共保存数据量：{save_count}")
                    print(f"没有标题或内容的数据量：{delete_count}")
                    print(f"重复数据：{dupli_count}")

                    # flag = input("是否需要再次读取文件夹内的文件（是输入y；否输入n）:").strip().lower()
                    # if flag != "y":
                    #     break
                    # now_time = input("请输入需要读取文件的截止日期：").strip()

                # 保存最终结果
                os.makedirs(output_path, exist_ok=True)
                self.dealfile.write_json_list(id, output_path, list(url_to_content.values()))
            except KeyboardInterrupt as e:

                # 保存最终结果
                os.makedirs(output_path, exist_ok=True)
                self.dealfile.write_json_list(id, output_path, list(url_to_content.values()))

        except Exception as e:
            print(f"转换json数组出错：{e}")
        finally:
            # 清理锁
            if hasattr(self, '_lock'):
                del self._lock


    @staticmethod
    def _process_file_wrapper(file_info, now_time, output_path, target_folder):
        """包装器函数，在每个进程中创建实例和加载模型"""
        try:
            # 在每个进程中创建实例
            processor = DictToArray()
            # 在进程内加载模型
            model = processor._load_model_once()
            # 调用处理函数
            return processor._process_file(file_info, now_time, output_path, target_folder, model)
        except Exception as e:
            print(f"包装器函数出错: {e}")
            return {"action": "error", "file": file_info[0], "error": str(e)}



# 线程池版本的修正（如果不想用进程池）
# def merge_json_files_by_url(self, id, output_path, target_folder, path1, path2=None, path3=None,
#                                        path4=None,
#                                        path5=None):
#     """线程池版本的合并函数"""
#     path_list = [path for path in [path1, path2, path3, path4, path5] if path]
#     delete_count = 0
#     save_count = 0
#     dupli_count = 0
#     url_to_content = {}
#     now_time = input("请输入需要读取文件的截止日期：")
#
#     # 在主线程加载模型
#     model = self._load_model_once()
#
#     try:
#         while True:
#             all_files = []
#             for path in path_list:
#                 os.makedirs(path, exist_ok=True)
#                 type_classification = os.path.basename(path)
#                 files = glob.glob(f"{path}/*.json")
#                 for file in files:
#                     all_files.append((file, type_classification))
#
#             print(f"找到 {len(all_files)} 个文件需要处理...")
#             batch_size = 1000  # 控制每批处理的文件数
#             for i in range(0, len(all_files), batch_size):
#                 batch = all_files[i:i + batch_size]
#                 with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
#                     futures = []
#                     for file_info in batch:
#                         # 注意：这里传递正确的参数顺序
#                         futures.append(
#                             executor.submit(
#                                 self._process_file,
#                                 file_info,
#                                 now_time,  # 正确的now_time参数
#                                 output_path,
#                                 target_folder,
#                                 model  # 传递已加载的模型
#                             )
#                         )
#
#                     for future in as_completed(futures):
#                         try:
#                             result = future.result()
#                             if result["action"] == "delete":
#                                 delete_count += 1
#                                 if os.path.exists(result["file"]):
#                                     os.remove(result["file"])
#                                     print(f'已经删除无内容标题文件：{result["file"]}')
#                             elif result["action"] == "move":
#                                 if not os.path.exists(result["dest"]):
#                                     os.makedirs(result["dest"], exist_ok=True)
#                                 if os.path.exists(result["file"]):
#                                     shutil.move(result["file"], result["dest"])
#                                     print(f"{os.path.basename(result['file'])} -> {os.path.basename(result['dest'])}")
#
#                             elif result["action"] == "move_lang":
#                                 if os.path.exists(result["file"]):
#                                     shutil.move(result["file"], result["dest"])
#                                     print(f"{os.path.basename(result['file'])} -> {os.path.basename(result['dest'])}")
#
#                             elif result["action"] == "keep":
#                                 if result["url"] not in url_to_content:
#                                     save_count += 1
#                                     url_to_content[result["url"]] = result["content"]
#                                     if not os.path.exists(target_folder):
#                                         os.makedirs(target_folder, exist_ok=True)
#                                     if os.path.exists(result["file"]):
#                                         shutil.move(result["file"], target_folder)
#                                         print(f"{os.path.basename(result['file'])} -> {os.path.basename(target_folder)}")
#                                 else:
#                                     if os.path.exists(result["file"]):
#                                         os.remove(result["file"])
#                                         print(f'已经删除重复文件：{result["file"]}')
#                                         dupli_count += 1
#
#                         except Exception as e:
#                             print(f"处理结果时出错: {e}")
#
#             print(f"共保存数据量：{save_count}")
#             print(f"没有标题或内容的数据量：{delete_count}")
#             print(f"重复数据：{dupli_count}")
#
#             flag = input("是否需要再次读取文件夹内的文件（是输入y；否输入n）:").strip().lower()
#             if flag != "y":
#                 break
#             now_time = input("请输入需要读取文件的截止日期：").strip()
#
#         # 保存最终结果
#         os.makedirs(output_path, exist_ok=True)
#         self.dealfile.write_json_list(id, output_path, list(url_to_content.values()))
#
#     except Exception as e:
#         print(f"转换json数组出错：{e}")
#     finally:
#         # 清理锁
#         if hasattr(self, '_lock'):
#             del self._lock



#
#
# from utils.file_io import DealFile
# import os
# import glob
# import shutil
# from datetime import datetime
# from tools.classificate_domain import AgricultureClassifier
# import fasttext
#
# class DictToArray:
#     def __init__(self):
#         self.dealfile = DealFile()
#         self.model = fasttext.load_model(r'D:\Scrapy\models\lid\lid.176.ftz')
#
#     def merge_json_files_by_url(self, id, output_path, target_folder,path1, path2=None, path3=None, path4=None, path5=None):
#         """合并两个文件夹下的JSON文件，按URL去重"""
#         path_list = [path for path in [path1, path2, path3, path4, path5] if path]
#         delete_count = 0
#         save_count = 0
#         dupli_count = 0
#         url_to_content = {}
#         now_time = input("请输入需要读取文件的截止日期：")
#
#         try:
#             while True:
#                 for path in path_list:
#                     os.makedirs(path,exist_ok=True)
#                     for file in glob.iglob(f"{path}/*.json"):
#                         time = os.path.getmtime(file)
#                         modified_date = datetime.fromtimestamp(time)
#                         compare_time = datetime.strptime(now_time,'%Y-%m-%d %H:%M:%S')
#
#                         if modified_date < compare_time:
#                             filename = os.path.basename(file)
#                             dir_path = os.path.dirname(file)
#
#                             content = self.dealfile.read_json(filename, dir_path)
#
#                             if content["title"] is None or content["content"] is None : # or len(content["content"]) < 100
#                                 os.makedirs(output_path,exist_ok=True)
#                                 self.dealfile.write_txt(f"no_title.txt", output_path, content["url"] + '\n', "a")
#                                 delete_count += 1
#                                 os.remove(file)
#                                 continue
#
#                             # 分类
#                             classifier = AgricultureClassifier()
#                             classifier_result = classifier.classify(content["title"], content["content"])
#                             type_classification = os.path.basename(path)
#                             if classifier_result.domain_name != type_classification:
#                                 others_folder = os.path.join(os.path.dirname(path),classifier_result.domain_name)
#                                 shutil.move(file, others_folder)
#                                 print(f"{file} -> {classifier_result.domain_name}")
#                                 continue
#
#                             con = content["title"]+content["content"]
#                             clean_con = "".join(con.split())
#
#                             # 检测语言
#                             predictions = self.model.predict(clean_con)
#                             label = predictions[0][0].replace('__label__', '')
#
#                             if label != content["language"]:
#                                 others_folder = fr"{os.path.dirname(path)}/再次分类"
#                                 os.makedirs(others_folder, exist_ok=True)
#                                 shutil.move(file,others_folder)
#                                 continue
#
#                             if content["url"] not in url_to_content:
#                                 save_count += 1
#                                 url_to_content[content["url"]] = content
#                                 os.makedirs(target_folder, exist_ok=True)
#                                 shutil.move(file, target_folder)
#                             else:
#                                 os.remove(file)
#                                 dupli_count += 1
#
#                 print(f"共保存数据量：{save_count}")
#                 print(f"没有标题或内容的数据量：{delete_count}")
#                 print(f"重复数据：{dupli_count}")
#
#
#                 flag = input("是否需要再次读取文件夹内的文件（是输入y；否输入n）:").strip().lower()
#                 if flag != "y":
#                     break
#                 now_time = input("请输入需要读取文件的截止日期：").strip()
#
#             os.makedirs(output_path, exist_ok=True)
#             self.dealfile.write_json_list(id, output_path, list(url_to_content.values()))
#
#         except Exception as e:
#             print("转换json数组出错：%s" % e)
