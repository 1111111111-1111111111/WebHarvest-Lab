class SearchKeyUrl:
    def __init__(selfself):
        pass

    def find_keyword_and_save_position(self,file_path, keyword, last_position=0):
        """
        查找关键字并保存位置，返回找到的关键字位置
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            f.seek(last_position)  # 从上次位置开始读取

            while True:
                current_position = f.tell()
                line = f.readline()

                if not line:  # 文件结束
                    break

                if keyword in line:
                    print(f"在位置 {current_position} 包含关键字: {line.strip()}")
                    # 返回当前行的结束位置，用于下次继续读取
                    next_position = f.tell()
                    return current_position, next_position, line.strip()

        return None, last_position, None


    def resume_reading_from_position(self,file_path, start_position):
        """
        从指定位置继续读取文件
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            f.seek(start_position)
            content = f.read()
            return content

    def return_position(self,filepath,keyword):
        current_pos, next_pos, found_line = self.find_keyword_and_save_position(filepath, keyword, 0)
        if current_pos is not None:
            remaining_content = self.resume_reading_from_position(filepath, next_pos)

            return current_pos,next_pos,remaining_content[:100]

if __name__ == "__main__":
    # 使用示例
    file_path = r"/scripts/多语言语料文本采集/高棉语URL2\no_read_urls.txt"

    # 第一次查找
    keyword = "nhat-ban-kazakhstan-ky-14-thoa-thuan-tri-gia-hon-15-ty-usd-post352039.vnp"


