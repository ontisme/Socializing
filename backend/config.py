import ruamel.yaml

import json
import os
from pathlib import Path

# 系統存檔主目錄
SYSTEM_FOLDER_PATH = os.path.join(os.getenv('APPDATA'), 'Socializing')
# 系統存檔位置
SYSTEM_CONFIG_PATH = os.path.join(SYSTEM_FOLDER_PATH, 'config.json')
# 瀏覽器裝置Profile位置
PROFILE_FOLDER_PATH = os.path.join(SYSTEM_FOLDER_PATH, 'BrowserCache')
# 瀏覽器裝置的設定檔存檔位置
PROFILE_CONFIG_FOLDER_PATH = os.path.join(SYSTEM_FOLDER_PATH, 'BrowserProfile')
# 瀏覽器裝置的備份檔存檔位置
PROFILE_BACKUP_FOLDER_PATH = os.path.join(SYSTEM_FOLDER_PATH, 'BrowserBackup')
# 瀏覽器主程式位置
BROWSER_BIN_PATH = os.path.join(SYSTEM_FOLDER_PATH, 'BrowserBin')
# 瀏覽器主程式位置
BROWSER_BIN_WIN_PATH = os.path.join(BROWSER_BIN_PATH, 'chrome-win')
# 日誌位置
LOG_FOLDER_PATH = os.path.join(SYSTEM_FOLDER_PATH, 'Logs')

# Script位置
SCRIPT_FOLDER_PATH = os.path.join(SYSTEM_FOLDER_PATH, 'BrowserScript')
# 腳本列表
SCRIPT_URL_LIST = [
    "https://socializing.sakurafb.cc/scripts/facebook.py",
    "https://socializing.sakurafb.cc/scripts/facebook_get_profile.py"
]


def dict_get(d, keys, default=None):
    """
    Get values in dictionary safely.
    https://stackoverflow.com/questions/25833613/safe-method-to-get-value-of-nested-dictionary

    Args:
        d (dict):
        keys (str, list): Such as `Scheduler.NextRun.value`
        default: Default return if key not found.

    Returns:

    """
    if isinstance(keys, str):
        keys = keys.split('.')
    assert type(keys) is list
    if d is None:
        return default
    if not keys:
        return d
    return dict_get(d.get(keys[0]), keys[1:], default)


def dict_set(d, keys, value):
    """
    Set value into dictionary safely, imitating deep_get().
    """
    if isinstance(keys, str):
        keys = keys.split('.')
    assert type(keys) is list
    if not keys:
        return value
    if not isinstance(d, dict):
        d = {}
    d[keys[0]] = dict_set(d.get(keys[0], {}), keys[1:], value)
    return d


def dict_merge(old, new):
    for key, value in new.items():
        if isinstance(value, dict):
            if key in old:
                dict_merge(old[key], value)
            else:
                old[key] = value
        else:
            if key not in old:
                old[key] = value

    return old


def dict_pop(d, keys, default=None):
    """
    Pop value from dictionary safely, imitating deep_get().
    """
    if isinstance(keys, str):
        keys = keys.split('.')
    assert type(keys) is list
    if not isinstance(d, dict):
        return default
    if not keys:
        return default
    elif len(keys) == 1:
        return d.pop(keys[0], default)
    return dict_pop(d.get(keys[0]), keys[1:], default)


def dict_default(d, keys, value):
    """
    Set default value into dictionary safely, imitating deep_get().
    Value is set only when the dict doesn't contain such keys.
    """
    if isinstance(keys, str):
        keys = keys.split('.')
    assert type(keys) is list
    if not keys:
        if d:
            return d
        else:
            return value
    if not isinstance(d, dict):
        d = {}
    d[keys[0]] = dict_default(d.get(keys[0], {}), keys[1:], value)
    return d


def dict_iter(data, depth=0, current_depth=1):
    """
    Iter a dictionary safely.

    Args:
        data (dict):
        depth (int): Maximum depth to iter
        current_depth (int):

    Returns:
        list: Key path
        Any:
    """
    if isinstance(data, dict) \
            and (depth and current_depth <= depth):
        for key, value in data.items():
            for child_path, child_value in dict_iter(value, depth=depth, current_depth=current_depth + 1):
                yield [key] + child_path, child_value
    else:
        yield [], data


# Profile

def get_profile_config_template():
    return {
        "index": 1,
        "profile": {
            "name": "default",
        },
        "facebook": {
            "name": "default",
            "user_id": ""
        },
        "tiktok": {
            "name": "default",
            "user_id": ""
        }
    }


def save_profile_config(data):
    """存模擬器設定檔(Profile) 至 ./config/profile/"""
    index = dict_get(data, "index")
    os.makedirs(PROFILE_CONFIG_FOLDER_PATH, exist_ok=True)
    config_path = os.path.join(PROFILE_CONFIG_FOLDER_PATH, f'{index}.json')

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)


def load_profile_config(index):
    """存模擬器設定檔(Profile) 至 ./config/profile/"""

    config_path = os.path.join(PROFILE_CONFIG_FOLDER_PATH, f'{index}.json')
    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            my_data = json.load(f)
            default_data = get_profile_config_template()
            dict_merge(my_data, default_data)
            return my_data
    else:
        mydata = get_profile_config_template()
        mydata['index'] = index


def delete_profile_config(index):
    """刪除設定檔"""
    config_path = os.path.join(PROFILE_CONFIG_FOLDER_PATH, f"{index}.json")
    # 檔案路徑
    file = Path(config_path)
    try:
        file.unlink()
        return True
    except OSError as e:
        print("Get Error: %s : %s" % (file, e.strerror))

    return False


# System

def get_system_config_template():
    return {
        "profile": {
            "path": os.path.join(SYSTEM_FOLDER_PATH, 'BrowserCache')
        }
    }


def save_system_config(data):
    config_dir = os.path.dirname(SYSTEM_CONFIG_PATH)
    os.makedirs(config_dir, exist_ok=True)

    with open(SYSTEM_CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


def load_system_config():
    if os.path.isfile(SYSTEM_CONFIG_PATH):
        with open(SYSTEM_CONFIG_PATH, "r") as f:
            my_data = json.load(f)
            default_data = get_system_config_template()
            dict_merge(my_data, default_data)
            return my_data
    else:
        return get_system_config_template()


def delete_system_config():
    # 檔案路徑
    file = Path(SYSTEM_CONFIG_PATH)
    try:
        file.unlink()
    except OSError as e:
        print("Get Error: %s : %s" % (file, e.strerror))
