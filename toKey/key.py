from utils.search_key import SearchKeyUrl
search_keys = SearchKeyUrl()
file_path = r"D:\Scrapy\scripts\多语言语料文本采集\越南语URL\vi_URL1_1.txt"
keyword = "https://fili.vn/2025/10/co-may-in-tien-cua-cac-hang-hang-khong-737-1365176.htm"
current_pos, next_pos, remaining_content = search_keys.return_position(file_path, keyword)
print(f"关键字在读取的文件位置: {current_pos}，接下来读取的位置: {next_pos}，改读取的内容: {remaining_content}")
