import asyncio
import os
import sys
import threading

from config import load_system_config, save_system_config
from fastapi import FastAPI

from server.configure import configure_router
from server.services.client import get_scripts
from utils.logger import server_logger

sys.stdout = open(os.devnull, 'w')
def create_app():
    _app = FastAPI()
    configure_router(_app)

    # @_app.on_event('startup')
    # def init_scheduler():
    #     scheduler = BackgroundScheduler()
    #     scheduler.add_job(sakura_client.loop_event, 'cron', second='*/2')
    #     scheduler.start()
    #
    return _app


app = create_app()

# sakura_client = SakuraClient("PythonTest")
my_config = load_system_config()
save_system_config(my_config)


server_logger.info("正在啟動伺服器...")
server_logger.info("Document：http://127.0.0.1:34567/docs")
asyncio.run(get_scripts())

try:
    import uvicorn as uvicorn
    uvicorn.run(app, host="0.0.0.0", port=34567)
except OSError as e:
    if "[WinError 10048]" in e:
        server_logger.error("Port 已被占用，有可能伺服器已經啟動，勿重複啟動！")
        exit(0)
