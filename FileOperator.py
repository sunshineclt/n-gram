# 封装了以日期为文件名的文件操作
from os.path import getsize


class FileOperator(object):
    # 存储文件名的基础文件名,最终存储形式类似./raw_data/data_2004_07_04.txt
    SAVE_PATH = './raw_data/data'

    # 用日期初始化文件操作类
    def __init__(self, date, mode):
        self.date_str = date.strftime('_%Y_%m_%d')
        self.file_name = self.__class__.SAVE_PATH + self.date_str + ".txt"
        self.file_object = open(self.file_name, mode)

    # 读取文件内容
    def readFile(self):
        return self.file_object.read()

    # 写入文件内容
    def writeFile(self, data_to_save):
        self.file_object.write(data_to_save)

    # 关闭文件
    def closeFile(self):
        self.file_object.close()

    # 获取文件的大小
    def getFileSize(self):
        return getsize(self.file_name)
