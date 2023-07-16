from fastapi import APIRouter
from server.schemas.base.response import response_ok
from server.services import profile

router = APIRouter(prefix='/profile', tags=['配置'])


@router.post('/add')
async def add_profile(profile_config=None):
    return response_ok(data=await profile.add_profile(profile_config))


@router.get('/list')
async def list_profile():
    profiles = await profile.list_profile()
    data = {
        "list": profiles,
        "total": len(profiles)
    }
    return response_ok(data=data)


@router.post('/del')
async def del_profile(profile_index: int):
    return response_ok(data=await profile.del_profile(profile_index))


@router.post('/sync/chrome')
async def sync_profile_from_chrome():
    return response_ok(data=await profile.sync_profile_from_chrome())
