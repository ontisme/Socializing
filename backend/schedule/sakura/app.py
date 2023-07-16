import queue

import requests

from utils.task_manager import TaskManager


class SakuraAPI:
    sakura_host = "https://sakurafb.cc/SakuraFacebook"  # 後臺域名
    get_task = f"{sakura_host}/webService/getTask"  # 取得工作
    end_task = f"{sakura_host}/webService/endTask"  # 結束工作
    get_task_type = f"{sakura_host}/webService/getTaskType"  # 取得工作類型
    offline = f"{sakura_host}/webService/offlineFacebook"  # 機台下線
    online = f"{sakura_host}/webService/onlineFacebook"  # 機台上線
    delete_facebook_user = f"{sakura_host}/webService/deleteFacebookUser"  # 機台上線


class SakuraClient:
    def __init__(self, machine_id: str, max_concurrent_tasks: int = 10):
        self.ses = requests.Session()
        self.machine_id = machine_id
        self.task_manager = TaskManager(max_concurrent_tasks=max_concurrent_tasks)
        self.init()

    def init(self):
        """
        初始化
        """
        self.ses.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62"
        })

    def get_task(self):
        """
        取得工作
        """
        params = {
            "machineId": self.machine_id,
            "taskId": ""
        }
        return self.ses.post(SakuraAPI.get_task, json=params).json()

    def end_task(self, task_id: str):
        """
        結束工作
        """
        params = {
            "machineId": self.machine_id,
            "taskId": task_id
        }
        return self.ses.post(SakuraAPI.end_task, json=params).json()

    def get_task_type(self):
        """
        取得工作類型
        """
        params = {
            "machineId": self.machine_id,
            "taskId": ""
        }
        return self.ses.post(SakuraAPI.get_task_type, json=params).json()

    def offline(self):
        """
        機台下線
        """
        params = {
            "machineId": self.machine_id,
            "taskId": ""
        }
        return self.ses.post(SakuraAPI.offline, json=params).json()

    def online(self):
        """
        機台上線
        """
        params = {
            "machineId": self.machine_id,
            "taskId": ""
        }
        return self.ses.post(SakuraAPI.online, json=params).json()

    def delete_facebook_user(self, facebook_id: str):
        """
        刪除用戶
        """
        params = {
            "machineId": self.machine_id,
            "facebookId": facebook_id
        }
        return self.ses.post(SakuraAPI.delete_facebook_user, json=params).json()

    def update_facebook_user(self):
        """
        更新用戶
        """


    def loop_event(self):
        tasks = self.get_task()
        # {'machineId': 'PythonTest', 'taskList': [], 'type': 'getTask'}
        if tasks and "taskList" in tasks:
            for i in tasks["taskList"]:
                self.task_manager.add_task(i["taskList"])

