import os

import requests

from config import SCRIPT_URL_LIST, SCRIPT_FOLDER_PATH
from utils.logger import server_logger


async def get_scripts():
    """取得所有腳本"""
    server_logger.info("正在更新腳本...")
    os.makedirs(SCRIPT_FOLDER_PATH, exist_ok=True)
    ses = requests.session()
    # 下載腳本到 SCRIPT_FOLDER_PATH
    for url in SCRIPT_URL_LIST:
        filename = url.split('/')[-1]
        r = ses.get(url)

        server_logger.info(f"更新腳本：{filename}")
        download_path = f"{SCRIPT_FOLDER_PATH}\\{filename}"

        with open(download_path, 'wb') as f:
            f.write(r.content)
    server_logger.info("更新腳本完畢...")
