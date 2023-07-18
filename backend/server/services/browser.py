from core.webdriver import Webdriver
from server import server_global


async def list_browser():
    data = {
        "list": server_global.webdrivers,
        "total": len(server_global.webdrivers)
    }
    return data


async def start_browser(profile_index: int):
    if profile_index in server_global.webdrivers:
        if server_global.webdrivers[profile_index].driver_is_alive():
            return True

    server_global.webdrivers[profile_index] = Webdriver(profile_index)
    return True


async def status(profile_index: int):
    if profile_index not in server_global.webdrivers:
        return False

    condition_1 = server_global.webdrivers[profile_index].task_queue_list != []
    condition_2 = server_global.webdrivers[profile_index].driver_is_alive()
    condition_3 = server_global.webdrivers[profile_index].current_task_thread is not None

    print(f"\r\ntask_queue_list: {condition_1}\r\n", f"driver_is_alive: {condition_2}\r\n",
          f"task_thread: {condition_3}\r\n", f"Result: {(condition_1 or condition_2 or condition_3)}")
    return condition_1 or condition_2 or condition_3

    # print(f"\r\ntask_queue_list: {condition_1}\r\n", f"driver_is_alive: {condition_2}\r\n", f"Result: {(condition_1 or condition_2)}")
    # return condition_1 or condition_2


async def add_task(profile_index: int, script: str, params: dict):
    if profile_index not in server_global.webdrivers or server_global.webdrivers[profile_index].driver_is_alive():
        await start_browser(profile_index)

    webdriver = server_global.webdrivers[profile_index]

    webdriver.add_task(script, params)
    return True
