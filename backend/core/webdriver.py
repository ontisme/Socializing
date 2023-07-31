import json
import logging
import os
import re
import shutil
import threading
import time
import zipfile
from urllib.parse import unquote

import psutil as psutil
import requests
from nb_log import get_logger
from urllib3.exceptions import ProtocolError

import config
from utils.webdriver_manager import get_chrome_driver

import undetected_chromedriver as uc


# from selenium.webdriver.chrome.service import Service
# from selenium import webdriver as uc


class Webdriver:
    def __init__(self, profile_index=None):
        self.profile_index = profile_index
        self.profile_dir = f'{config.PROFILE_FOLDER_PATH}\\{self.profile_index}'
        self.profile_backup_dir = f'{config.PROFILE_BACKUP_FOLDER_PATH}\\{self.profile_index}.zip'

        self.config = config.load_profile_config(self.profile_index)

        self.log_path = config.LOG_FOLDER_PATH + f'\\Browser\\{self.profile_index}'
        os.makedirs(self.log_path, exist_ok=True)
        self.logger = get_logger(f'Browser {self.profile_index}',
                                 log_filename=f'{self.log_path}\\client.log',
                                 is_add_stream_handler=True,
                                 formatter_template=logging.Formatter(
                                     f'%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s - "%(pathname)s:%(lineno)d"',
                                     "%Y-%m-%d %H:%M:%S"))
        self.driver: uc.Chrome = None

        self.task_queue_list = []  # 存放要執行的腳本
        self.current_task_thread = None  # 目前執行中的線程
        self.task_queue_loop_thread = threading.Thread(target=self.task_queue_loop)
        self.task_queue_loop_thread.setDaemon(True)
        self.task_queue_loop_thread.start()

        self.driver_pid = 0
        self.browser_pid = 0

    # 檢查裝置是否還活著
    def driver_is_alive(self):
        try:
            if self.driver is None:
                return False
            # Selenium
            # driver_process = psutil.Process(self.driver.service.process.pid)
            #
            # if driver_process.is_running():
            #     self.driver.quit()
            #     return True

            # UC
            driver_process = psutil.Process(self.driver.service.process.pid)
            browser_process = psutil.Process(self.driver.browser_pid)

            if driver_process.is_running():
                if browser_process.is_running():
                    return True
            return False
        except:
            return False

    def driver_quit(self, backup_profile=True):
        try:
            self.terminate_process(self.driver_pid)
            self.terminate_process(self.browser_pid)
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("關閉裝置或是瀏覽器失敗")
        finally:
            self.driver = None
            self.driver_pid = 0
            self.browser_pid = 0
            if backup_profile:
                self.backup_profile()

    def terminate_process(self, pid):
        try:
            process = psutil.Process(pid)
            if process.is_running():
                process.kill()
        except:
            pass

    # 備份瀏覽器資料

    def backup_profile(self):
        try:
            self.logger.info("備份裝置")
            os.makedirs(config.PROFILE_BACKUP_FOLDER_PATH, exist_ok=True)
            profile_backup_dir = os.path.join(config.PROFILE_BACKUP_FOLDER_PATH, str(self.profile_index))

            # 刪除目標目錄（如果存在）
            if os.path.exists(profile_backup_dir):
                shutil.rmtree(profile_backup_dir)

            os.makedirs(profile_backup_dir)

            files_to_backup = [
                os.path.join(self.profile_dir, 'Local State'),
                os.path.join(self.profile_dir, 'Variations'),
                os.path.join(self.profile_dir, 'persisted_first_party_sets.json'),
                os.path.join(self.profile_dir, 'DevToolsActivePort'),
                os.path.join(self.profile_dir, 'Last Version'),
                os.path.join(self.profile_dir, 'Last Browser'),
                os.path.join(self.profile_dir, 'Default', 'History'),
                os.path.join(self.profile_dir, 'Default', 'History-journal'),
                os.path.join(self.profile_dir, 'Default', 'LOG'),
                os.path.join(self.profile_dir, 'Default', 'Bookmarks'),
                os.path.join(self.profile_dir, 'Default', 'Secure Preferences'),
                os.path.join(self.profile_dir, 'Default', 'Network'),
                os.path.join(self.profile_dir, 'Default', 'AutofillStrikeDatabase'),
                os.path.join(self.profile_dir, 'Default', 'blob_storage'),
                os.path.join(self.profile_dir, 'Default', 'BudgetDatabase'),
                os.path.join(self.profile_dir, 'Default', 'optimization_guide_hint_cache_store'),
                os.path.join(self.profile_dir, 'Default', 'optimization_guide_model_metadata_store'),
                os.path.join(self.profile_dir, 'Default', 'coupon_db'),
                os.path.join(self.profile_dir, 'Default', 'Extension Rules'),
                os.path.join(self.profile_dir, 'Default', 'Extension State'),
                os.path.join(self.profile_dir, 'Default', 'Session Storage'),
                os.path.join(self.profile_dir, 'Default', 'Sessions'),
                os.path.join(self.profile_dir, 'Default', 'shared_proto_db'),
                os.path.join(self.profile_dir, 'Default', 'Site Characteristics Database'),
            ]

            for item_path in files_to_backup:
                if os.path.exists(item_path):
                    dest_path = os.path.join(profile_backup_dir, os.path.relpath(item_path, self.profile_dir))
                    if os.path.isdir(item_path):
                        shutil.copytree(item_path, dest_path)
                    else:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(item_path, dest_path)

            profile_backup_path = os.path.join(config.PROFILE_BACKUP_FOLDER_PATH, f'{self.profile_index}.zip')
            with zipfile.ZipFile(profile_backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                for root, dirs, files in os.walk(profile_backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        backup_zip.write(file_path, os.path.relpath(file_path, profile_backup_dir))

            if os.path.exists(self.profile_dir):
                shutil.rmtree(self.profile_dir)

            self.logger.info("備份裝置完成")
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("備份裝置失敗")

    # 還原瀏覽器資料
    def restore_profile(self):
        try:
            self.logger.info("還原裝置")
            if not os.path.isfile(self.profile_backup_dir):
                raise FileNotFoundError("備份檔案不存在")

            with zipfile.ZipFile(self.profile_backup_dir, 'r') as backup_zip:
                backup_zip.extractall(self.profile_dir)

            self.logger.info("裝置還原完成")
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("裝置還原失敗")

    def create_webdriver(self):
        """
        Creates a webdriver instance of uc.Chrome with specified options and configurations.

        Returns:
            A uc.Chrome instance.
        """
        # driver_path = get_chrome_driver()
        # version = get_chrome_version()
        self.logger.info("初始化裝置")
        self.restore_profile()
        options = self.add_webdriver_options()
        get_chrome_driver()
        try:
            # Selenium
            # services = Service(driver_path)
            # driver = uc.Chrome(options=options, service=services)
            # UC
            driver = uc.Chrome(options=options,
                               user_data_dir=self.profile_dir,
                               browser_executable_path=os.path.join(config.BROWSER_BIN_WIN_PATH, "chrome.exe"),
                               )
            self.driver_pid = driver.service.process.pid
            self.browser_pid = driver.browser_pid
            return driver

        except ProtocolError as e:
            self.logger.error("WebDriver 創建失敗，發生異常停止運行腳本")
            self.logger.exception(e)
            return False
        except Exception as e:
            error_msg = str(e)
            self.logger.exception(e)
            if "This version of ChromeDriver only supports Chrome version" in error_msg:
                current_browser_version = re.search(r"Current browser version is (\d+\.\d+\.\d+\.\d+)", error_msg)
                supported_chrome_version = re.search(r"supports Chrome version (\d+)", error_msg)

                if current_browser_version and supported_chrome_version:
                    current_browser_version = current_browser_version.group(1)
                    supported_chrome_version = supported_chrome_version.group(1)
                    print("當前瀏覽器版本：", current_browser_version)
                    print("當前 Chrome Driver 版本：", supported_chrome_version)
                    print("正在更新 Chrome Driver 版本")
                    get_chrome_driver(True)
                    print("已更新 Chrome Driver 版本，請重新啟動")
                    exit(0)

    def add_webdriver_options(self):
        """
        Adds options to a Chrome webdriver instance.

        Args:
        - options: An instance of ChromeOptions to which the options will be added.

        Returns:
        - An instance of ChromeOptions with the added options.

        Raises:
        - None
        """
        options = uc.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=540,960")
        options.add_argument('--disable-audio-output')
        options.add_argument('--disable-notifications')
        # options.add_argument("--auto-open-devtools-for-tabs")  # automatically open dev tools on every new tab
        options.add_argument("--disable-gpu")
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        options.add_argument(f"--profile-directory=Default")

        return options

    def run_script(self, script: str = None, params: dict = None):
        if not self.driver:
            try:
                self.driver = self.create_webdriver()
                if not self.driver:
                    self.logger.error("初始化裝置失敗")
                    return False
            except Exception as e:
                self.logger.error("WebDriver 創建失敗，發生異常停止運行腳本")
                self.logger.exception(e)
                return False
        # else:
        #     if not self.driver.service.is_connectable():
        #         self.driver.start_client()
        self.logger.info("初始化裝置成功")
        script_path = os.path.join(config.SCRIPT_FOLDER_PATH, script)
        if os.path.isfile(script_path):  # 判断是否为文件路径
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()  # 读取文件内容

        if "start" in script:
            # 提取 """Start""" 到 """End""" 之间的内容
            start_marker = '"""Start"""'
            end_marker = '"""End"""'

            start_index = script.find(start_marker) + len(start_marker)
            end_index = script.find(end_marker)

            extracted_content = script[start_index:end_index]

            # 格式化提取的内容
            lines = extracted_content.split('\n')
            lines = lines[1:len(lines) - 1]
            script = '\n'.join(line[8:] if len(line) >= 8 else line for line in lines)
            script = script.replace('\"params_text_here\"', json.dumps(params)[1:-1])
        try:
            exec(script)
        except Exception as e:
            self.logger.error("run_script 發生異常停止運行腳本")
            self.logger.exception(e)
            self.driver_quit()

    def task_queue_loop(self):
        """循環等待任務"""
        while True:
            if not self.current_task_thread:
                if self.task_queue_list:
                    task = self.task_queue_list.pop(0)
                    self.current_task_thread = threading.Thread(target=self.run_script, args=(task[0], task[1],))
                    self.current_task_thread.setDaemon(True)
                    self.current_task_thread.start()
                else:
                    time.sleep(1)  # 如果沒有排程，就循環等待

            if self.current_task_thread and not self.current_task_thread.is_alive():
                self.current_task_thread = None

            time.sleep(1)

    def add_task(self, script, params):
        self.logger.info("新增任務")
        self.logger.info(f"腳本：{script}\r\n參數：{params}")
        self.task_queue_list.append([script, params])

    def save_config(self):
        config.save_profile_config(self.config)


if __name__ == '__main__':
    c = Webdriver(1)
    c.driver = c.create_webdriver()
    c.driver.get("https://fb.com/me")
    time.sleep(0.5)
    re_pattern = r'"profilePicLarge":{"uri":"(.+)"},"profilePicMedium"'
    match_guides = re.findall(re_pattern, c.driver.page_source)
    img_url = unquote(match_guides[0].replace("\\/", "/"))
    # 取得圖片的二進位資料
    response = requests.get(img_url)
    image_data = response.content
    # 將圖片二進位資料寫入檔案
    with open("profile.jpg", "wb") as file:
        file.write(image_data)
    c.driver_quit()
