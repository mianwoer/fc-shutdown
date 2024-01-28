import paramiko
import logging
import sys
import time
import os
import configparser

def get_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fc_logger = logging.getLogger('fc-shutdown')
    return fc_logger


if __name__ == '__main__':
    """
       使用python直接运行脚本，可以使用  __file__
       如果打包成exe在windows运行，需要使用  os.path.realpath(sys.argv[0])
       """
    # project_path = os.path.dirname(__file__)
    project_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    start_time = time.time()  # 记录开始时间
    """生成日志对象"""
    logger = get_logger()

    if True:
        """读取配置文件"""
        config = configparser.ConfigParser()
        config.read(os.path.join(project_path, 'config.ini'), encoding='utf-8')
        remote_ip = config['config']['remote_ip']
        ssh_port = config['config']['ssh_port']
        user = config['config']['user']
        passwd = config['config']['passwd']
        logger.info("""开始向远程服务器 \"%s\" 发送关机命令  """, remote_ip)

    """远程登录关闭服务器"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, ssh_port, user, passwd)
        stdin1, ret, stderr1 = ssh.exec_command("shutdown -h now")
    except:
        logger.info("服务器ssh连接异常，请检查配置或网络联通情况")
        raise
    end_time = time.time()
    logger.info("发送关机命令完毕，耗时 %.2f秒" % (end_time - start_time))
