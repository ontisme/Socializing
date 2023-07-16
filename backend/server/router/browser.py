import os
import re
from fastapi import APIRouter

from server.schemas.base.response import response_ok
from server.schemas.browser import AddTaskIn
from server.services import browser

router = APIRouter(prefix='/browser', tags=['瀏覽器'])


@router.post('/start')
async def start_browser(profile_index: int):
    await browser.start_browser(profile_index)
    return response_ok()


@router.post('/add_task')
async def add_task(add_task_in: AddTaskIn):
    await browser.add_task(add_task_in.profile_index, add_task_in.script, add_task_in.params)
    return response_ok()


@router.get('/status')
async def status(profile_index: int):
    return response_ok(data=await browser.status(profile_index))


@router.get('/list')
async def list_browser():
    return response_ok(data=await browser.list_browser())
