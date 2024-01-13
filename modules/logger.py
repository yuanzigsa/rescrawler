import os
import logging
from logging.handlers import TimedRotatingFileHandler
from colorlog import ColoredFormatter  # 导入ColoredFormatter

log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = os.path.join(log_directory, '../log/crealer.log')

# 配置控制台输出的日志格式和颜色
console_formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'INFO': 'cyan',
        'ERROR': 'red',
        'WARNING': 'yellow',
        'CRITICAL': 'bold_red',
    }
)

# 配置文件输出的日志格式
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建并配置日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建并配置控制台处理程序
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 创建并配置文件处理程序
file_handler = TimedRotatingFileHandler(filename=log_file_path, when='midnight', interval=1, backupCount=30, encoding='utf-8')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)