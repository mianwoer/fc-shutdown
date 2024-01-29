import multiprocessing

import paramiko
import logging
import sys
import time
import os
import configparser

def get_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - [%(process)d] - %(message)s')
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

if __name__ == '__main__':
    """
       使用python直接运行脚本，可以使用  __file__
       如果打包成exe在windows运行，需要使用  os.path.realpath(sys.argv[0])
       """
    project_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    start_time = time.time()  # 记录开始时间
    """生成日志对象"""
    logger = get_logger()

    if os.path.exists("./config.ini"):
        """读取配置文件"""
        config = configparser.ConfigParser()
        config.read(os.path.join(project_path, 'config.ini'), encoding='utf-8')
        remote_ip = config['config']['remote_ip']
        ssh_port = config['config']['ssh_port']
        user = config['config']['user']
        passwd = config['config']['passwd']

        if "," in remote_ip:
            remote_ip = remote_ip.split(",")
        print(remote_ip, type(remote_ip))
        logger.info("""开始向远程服务器 \"%s\" 发送关机命令  """, remote_ip)

        #
        for ip in remote_ip:
            pool = multiprocessing.Pool()
            pool_tasks = []
            # task = pool.apply_async(TestSsh, args=(ip, ssh_port, user, passwd), callback=LogTestSSh, error_callback=error_callback_func)
            #这里apply_async不需要回调函数，没有数据需要处理;
            #不需要error回调函数，异常在子进程中已处理好
            task = pool.apply_async(PowerOff, args=(ip, ssh_port, user, passwd))
            pool_tasks.append(task)
        [_.wait() for _ in pool_tasks]
        pool.close()
        pool.join()
    else:
        logger.error("未找到配置文件\"config.ini\"")
    end_time = time.time()
    logger.info("发送关机命令完毕，耗时 %.2f秒" % (end_time - start_time))
