import schedule
import time
import datetime

def one():
    # 在这里写下你想要执行的函数的代码
    print(f"{datetime.datetime.now()}Your function is executed at a specific time.111111111111")

def two():
    # 在这里写下你想要执行的函数的代码
    print(f"{datetime.datetime.now()}Your function is executed at a specific time.222222222222")


# 设置每天的执行时间，例如每天的10:30执行
schedule.every().day.at("18:51").do(one)
schedule.every().day.at("18:52").do(two)


while True:
    # 检查是否有要执行的任务
    schedule.run_pending()
    time.sleep(1)  # 每秒钟检查一次

# 注意：这个程序会一直运行，你可以手动停止它或者根据你的需求修改程序的退出条件。
