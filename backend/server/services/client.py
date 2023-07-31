import os
from zipfile import ZipFile

import requests

from config import SCRIPT_URL_LIST, SCRIPT_FOLDER_PATH, BROWSER_BIN_PATH, BROWSER_BIN_WIN_PATH
from utils.logger import server_logger


async def get_scripts():
    """取得所有腳本"""
    # server_logger.info("正在更新腳本...")
    os.makedirs(SCRIPT_FOLDER_PATH, exist_ok=True)
    ses = requests.session()
    # 下載腳本到 SCRIPT_FOLDER_PATH
    for url in SCRIPT_URL_LIST:
        filename = url.split('/')[-1]
        r = ses.get(url)

        # server_logger.info(f"更新腳本：{filename}")
        download_path = f"{SCRIPT_FOLDER_PATH}\\{filename}"

        with open(download_path, 'wb') as f:
            f.write(r.content)
    server_logger.info("更新腳本完畢...")


async def get_browser_bin(force_update=False):
    """取得瀏覽器主程式"""

    # 檢查 BROWSER_BIN_PATH 是否有檔案
    if not force_update and os.path.exists(os.path.join(BROWSER_BIN_WIN_PATH, "chrome.exe")):
        return

    # 如果沒有檔案，則下載瀏覽器主程式
    server_logger.info("正在更新瀏覽器主程式...")
    os.makedirs(BROWSER_BIN_PATH, exist_ok=True)
    ses = requests.session()
    download_url = "https://github.com/ungoogled-software/ungoogled-chromium-windows/releases/download/114.0.5735.199-1.1/ungoogled-chromium_114.0.5735.199-1.1_windows_x64.zip"
    r = ses.get(download_url)

    if r.status_code != 200:
        server_logger.error("無法下載瀏覽器主程式，下載連結回傳非 200 狀態碼")
        return

    # 下載瀏覽器主程式到暫存檔
    temp_zip_path = os.path.join(BROWSER_BIN_PATH, "bin.zip")  # 更換成實際的暫存檔案路徑
    with open(temp_zip_path, 'wb') as f:
        f.write(r.content)

    # 解壓縮到 BROWSER_BIN_PATH
    with ZipFile(temp_zip_path, 'r') as z:
        z.extractall(BROWSER_BIN_PATH)

    # 刪除暫存檔案
    os.remove(temp_zip_path)

    # 修改符合條件的檔案名稱
    for filename in os.listdir(BROWSER_BIN_PATH):
        if filename.startswith("ungoogled"):
            os.rename(os.path.join(BROWSER_BIN_PATH, filename), os.path.join(BROWSER_BIN_PATH, "chrome-win"))

    # 關閉 session
    ses.close()

    server_logger.info("更新瀏覽器主程式完畢...")


async def startup_event():
    """啟動時，先更新"""
    await get_scripts()
    await get_browser_bin()
