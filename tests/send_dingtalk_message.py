import requests
import datetime

# 发送钉钉消息
def send_dingtalk_message(webhook, message):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "节点流量统计",
            "text": message
        }
    }
    response = requests.post(webhook, json=data, headers=headers)
    if response.status_code == 200:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送成功")
    else:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送失败，正在重试...")
        # 重试发送钉钉消息
        retry_count = 10  # 设置重试次数
        for i in range(retry_count):
            response = requests.post(webhook, json=data, headers=headers)
            if response.status_code == 200:
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送成功")
                break
            else:
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送失败，正在重试...")
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 重试发送钉钉消息失败")


webhook = "https://oapi.dingtalk.com/robot/send?access_token=52877c8d2b6ad2dad211585d0417f70202693c80ce343e0ad71958e3870d83b9"
message = "这是一条测试信息"

send_dingtalk_message(webhook, message)
