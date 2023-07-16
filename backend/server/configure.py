from fastapi import FastAPI

from server.router.browser import router as browser_router
from server.router.client import router as client_router
from server.router.profile import router as profile_router


def configure_router(app: FastAPI, prefix='/api'):
    app.include_router(browser_router, prefix=prefix)
    app.include_router(client_router, prefix=prefix)
    app.include_router(profile_router, prefix=prefix)

