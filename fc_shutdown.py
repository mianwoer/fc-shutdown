import ctypes
import multiprocessing

import paramiko
import logging
import sys
import time
import os
import configparser

import yaml


def get_logger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - [%(process)d] - %(message)s')
    fc_logger = logging.getLogger('fc-shutdown')

    # Create a console handler
    # console_handler = logging.StreamHandler()
    # fc_logger.addHandler(console_handler)

    # Create a file handler
    # if not os.path.exists("./log"):
    #     os.mkdir("./log")
    # file_handler = logging.FileHandler('./log/my_log.log')

    # fc_logger.addHandler(file_handler)
    return fc_logger


def PowerOff(ip, p, u, pw):
    logger_sub = get_logger()
    logger_sub.info("向服务器\"%s\"发送关机指令", ip)
    """远程登录关闭服务器"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, p, u, pw)
        # stdin1, ret, stderr1 = \
        ssh.exec_command("shutdown -h now")
    except:
        logger_sub.error("%s服务器ssh连接异常，请检查配置或网络联通情况", ip)


def read_yaml_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


# def error_callback_func(err):
#     logger.info(err)
"""
def TestSsh(ip, p, u, pw):
    logger_sub = get_logger()

    logger_sub.info("模拟向服务器\"%s\"发送bash指令", ip)
    # print("子进程----模拟发送bash指令...", ip, p, u, pw)
    time.sleep(3)
    # return ("模拟发送bash指令...", ip, p, u, pw)

def LogTestSSh(str):
    # logger = logging.getLogger(__name__)
    # logger.info(str)
    print(str)"""

def message_box(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

if __name__ == '__main__':
    # 新增下面一行代码即可打包多进程
    multiprocessing.freeze_support()
    """
       使用python直接运行脚本，可以使用  __file__
       如果打包成exe在windows运行，需要使用  os.path.realpath(sys.argv[0])
       """

    # 弹窗是否需要执行任务
    title = "提示"
    text = "确认是否关闭服务器？"
    style = 4 | 32  # 4表示是Yes/No对话框，32表示有图标
    result = message_box(title, text, style)
    if result != 6:  # 6表示用户点击了“Yes”按钮
        print("用户选择了取消任务")
        sys.exit()
    else:
        print("用户选择了执行任务")

    project_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    start_time = time.time()  # 记录开始时间
    """生成日志对象"""
    logger = get_logger()

    # 读取yml配置文件
    if os.path.exists("./config.yml"):
        config_file_path = './config.yml'
        config = read_yaml_config(config_file_path)     #读取为dict类型
        server_set = config["server_set"]
        if server_set:
            #服务器集合不为空
            logger.info("待关闭服务器ip为：%s",
                        [i["ip"] for i in server_set])
            pool = multiprocessing.Pool()
            pool_tasks = []
            for server in server_set:
                # 这里apply_async不需要回调函数，进程池没有数据需要返给主进程处理; 不需要error回调函数，异常在子进程中已处理好
                task = pool.apply_async(PowerOff, args=(server["ip"], server["ssh_port"], server["user"], server["passwd"]))
                pool_tasks.append(task)
            [_.wait() for _ in pool_tasks]
            pool.close()
            pool.join()
    else:
        logger.error("未找到配置文件\"config.yml\"")
    end_time = time.time()
    logger.info("发送关机命令完毕，耗时 %.2f秒" % (end_time - start_time))
    input("请按 Enter 键退出程序...")