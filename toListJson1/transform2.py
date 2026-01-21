from utils.to_list_json import DictToArray

import uuid

def main():
    # fb57cac6-e2de-4b80-982f-abf4b5a98a17
    # 0e0dc428-e047-4acd-abea-acc59bdd4c91
    id = f"{uuid.uuid4()}.json"
    # 种植业 | 渔业（水产业） | 休闲农业与乡村旅游业 | 设施农业 | 农产品贸易业
    # 农业职业教育 | 农业科技服务业 | 农业文化 | 畜牧业 | 农产品加工业
    path1 = r"D:\DATA\多语言语料文本采集\越南语\畜牧业"
    path2 = None
    path3=None
    path4=None
    path5=None
    target_folder = r"D:\DATA\多语言语料文本采集\越南语\总-畜牧业"
    output_path = r"D:\DATA\DATA\东盟十国特定领域文本采集\越南语\畜牧业"
    merge_data = DictToArray()
    merge_data.merge_json_files_by_url(id, output_path,target_folder,path1,path2,path3,path4,path5)


if __name__ == '__main__':
    main()
