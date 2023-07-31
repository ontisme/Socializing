import asyncio
import os
import re
import shutil
import time
import zipfile

import config
from server import server_global
from server.services.browser import add_task, status
from utils import webdriver_manager
from utils.logger import server_logger


async def list_profile():
    profiles = []
    try:
        for profile in os.listdir(config.PROFILE_CONFIG_FOLDER_PATH):
            if re.match(r"\d+\.json$", profile):
                profile_index = profile.replace('.json', '')
                a = config.load_profile_config(profile_index)
                profiles.append(a)
    except:
        pass

    return profiles


async def add_profile(profile_config=None):
    try:
        if profile_config is None:
            profile_index = await get_unused_profile_index()
            profile_config = config.get_profile_config_template()
            profile_config['index'] = profile_index

        config.save_profile_config(profile_config)

        return True
    except Exception as e:
        server_logger.exception(e)
        server_logger.error("新增配置檔失敗")
        return False


async def del_profile(profile_index: int):
    config.delete_profile_config(profile_index)
    return True


async def get_unused_profile_index():
    # 從 BrowserProfile 資料夾中遍歷尋找未使用的 profile index
    profile_index = 1
    while True:
        profile_dir = os.path.join(config.PROFILE_CONFIG_FOLDER_PATH, f"{profile_index}.json")
        if not os.path.exists(profile_dir):
            break
        profile_index += 1
    return profile_index


async def import_profile_from_chrome(profile_data: dict):
    """單獨備份 Chrome 資料夾中的資料到 BrowserProfile"""
    try:
        server_logger.info("備份裝置 => " + profile_data['dir'])
        os.makedirs(config.PROFILE_BACKUP_FOLDER_PATH, exist_ok=True)
        profile_index = await get_unused_profile_index()
        profile_backup_dir = os.path.join(config.PROFILE_BACKUP_FOLDER_PATH, str(profile_index))
        profile_root_dir = os.path.dirname(profile_data['dir'])

        # 新增 Browser Profile
        profile_config = config.get_profile_config_template()
        profile_config['index'] = profile_index
        res = await add_profile(profile_config)
        if res:
            # server_logger.info("備份裝置完成")
            pass
        else:
            server_logger.error("備份裝置失敗")

        await add_task(profile_index, "", {})

        while True:
            print("等待開啟瀏覽器")
            await asyncio.sleep(2)
            if await status(profile_index):
                await asyncio.sleep(2)
                server_global.webdrivers[profile_index].driver_quit(False)
                print("已關閉瀏覽器")
                break

            await asyncio.sleep(1)

        # 刪除目標目錄（如果存在）
        if os.path.exists(profile_backup_dir):
            shutil.rmtree(profile_backup_dir)

        os.makedirs(profile_backup_dir)
        os.makedirs(os.path.join(profile_backup_dir, 'Default'))

        files_to_backup = [
            [os.path.join(profile_root_dir, 'Local State'), os.path.join(profile_backup_dir, 'Local State')],
            [os.path.join(profile_root_dir, 'Variations'), os.path.join(profile_backup_dir, 'Variations')],
            [os.path.join(profile_root_dir, 'persisted_first_party_sets.json'),
             os.path.join(profile_backup_dir, 'persisted_first_party_sets.json')],
            [os.path.join(profile_root_dir, 'DevToolsActivePort'),
             os.path.join(profile_backup_dir, 'DevToolsActivePort')],
            [os.path.join(profile_root_dir, 'Last Version'), os.path.join(profile_backup_dir, 'Last Version')],
            [os.path.join(profile_root_dir, 'Last Browser'), os.path.join(profile_backup_dir, 'Last Browser')],
            [os.path.join(profile_data['dir'], 'History'), os.path.join(profile_backup_dir, 'Default', 'History')],
            [os.path.join(profile_data['dir'], 'History-journal'),
             os.path.join(profile_backup_dir, 'Default', 'History-journal')],
            [os.path.join(profile_data['dir'], 'LOG'), os.path.join(profile_backup_dir, 'Default', 'LOG')],
            [os.path.join(profile_data['dir'], 'Bookmarks'), os.path.join(profile_backup_dir, 'Default', 'Bookmarks')],
            [os.path.join(profile_data['dir'], 'Secure Preferences'),
             os.path.join(profile_backup_dir, 'Default', 'Secure Preferences')],
            [os.path.join(profile_data['dir'], 'Network'), os.path.join(profile_backup_dir, 'Default', 'Network')],
            [os.path.join(profile_data['dir'], 'AutofillStrikeDatabase'),
             os.path.join(profile_backup_dir, 'Default', 'AutofillStrikeDatabase')],
            [os.path.join(profile_data['dir'], 'blob_storage'),
             os.path.join(profile_backup_dir, 'Default', 'blob_storage')],
            [os.path.join(profile_data['dir'], 'BudgetDatabase'),
             os.path.join(profile_backup_dir, 'Default', 'BudgetDatabase')],
            [os.path.join(profile_data['dir'], 'optimization_guide_hint_cache_store'),
             os.path.join(profile_backup_dir, 'Default', 'optimization_guide_hint_cache_store')],
            [os.path.join(profile_data['dir'], 'optimization_guide_model_metadata_store'),
             os.path.join(profile_backup_dir, 'Default', 'optimization_guide_model_metadata_store')],
            [os.path.join(profile_data['dir'], 'coupon_db'), os.path.join(profile_backup_dir, 'Default', 'coupon_db')],
            [os.path.join(profile_data['dir'], 'Extension Rules'),
             os.path.join(profile_backup_dir, 'Default', 'Extension Rules')],
            [os.path.join(profile_data['dir'], 'Extension State'),
             os.path.join(profile_backup_dir, 'Default', 'Extension State')],
            [os.path.join(profile_data['dir'], 'Session Storage'),
             os.path.join(profile_backup_dir, 'Default', 'Session Storage')],
            [os.path.join(profile_data['dir'], 'Sessions'), os.path.join(profile_backup_dir, 'Default', 'Sessions')],
            [os.path.join(profile_data['dir'], 'shared_proto_db'),
             os.path.join(profile_backup_dir, 'Default', 'shared_proto_db')],
            [os.path.join(profile_data['dir'], 'Site Characteristics Database'),
             os.path.join(profile_backup_dir, 'Default', 'Site Characteristics Database')],
        ]

        for item_path in files_to_backup:
            if os.path.exists(item_path[0]):
                if os.path.isdir(item_path[0]):
                    shutil.copytree(item_path[0], item_path[1])
                else:
                    shutil.copy(item_path[0], item_path[1])

        profile_backup_path = os.path.join(config.PROFILE_BACKUP_FOLDER_PATH, f'{profile_index}.zip')
        with zipfile.ZipFile(profile_backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            for root, dirs, files in os.walk(profile_backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    backup_zip.write(file_path, os.path.relpath(file_path, profile_backup_dir))

    except Exception as e:
        server_logger.exception(e)
        server_logger.error("備份裝置失敗")


async def sync_profile_from_chrome():
    """同步 Chrome 所有的配置檔到 BrowserProfile"""
    chrome_path = webdriver_manager.CHROME
    if not chrome_path:
        server_logger.error("Chrome 可能沒有安裝")
        return False

    profile_path = os.path.join(chrome_path, "User Data")
    if not os.path.exists(profile_path):
        server_logger.error("Chrome 沒有 User Data 資料夾")
        return False

    # 尋找 profile_path 底下的資料夾，尋找開頭為 Profile 的資料夾，以及 Default 資料夾
    profile_folders = []
    for folder in os.listdir(profile_path):
        if folder.startswith("Profile") or folder == "Default":
            profile_dir = os.path.join(profile_path, folder)
            profile_name = folder
            profile_folders.append({
                "name": profile_name,
                "dir": profile_dir
            })

    if not profile_folders:
        server_logger.error("Chrome 沒有任何配置檔")
        return False

    # 將 profile_folders 複製到 BrowserCache 並
    for profile in profile_folders:
        await import_profile_from_chrome(profile)

    return True


if __name__ == '__main__':
    asyncio.run(sync_profile_from_chrome())
