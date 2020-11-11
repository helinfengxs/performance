import logging


class logs():
    # def __init__(self,fileName,level=logging.DEBUG):
    #     logging.basicConfig(filename=fileName,
    #                     format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level=level,
    #                     filemode='a', datefmt='%Y-%m-%d%I:%M:%S %p')
    def __init__(self,name):
        # 获取一个新日志
        logger = logging.getLogger()

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(name, encoding='utf-8')

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()

        # 定义一个模板
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 设置日志记录等级
        logger.setLevel(logging.DEBUG)

        # 把定义的模板绑定给创建的handler
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 指定要输出的方式
        logger.addHandler(fh)  # logger对象可以添加多个fh和ch对象
        logger.addHandler(ch)
    def debug(self,message):
        logging.debug(message)
    def info(self,message):
        logging.info(message)
    def error(self,message):
        logging.error(message)
    def warning(self,message):
        logging.warning(message)

    def __del__(self):
        class_name = self.__class__.__name__
        print(class_name, "销毁")