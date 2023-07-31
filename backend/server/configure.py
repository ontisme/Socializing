from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from server.router.browser import router as browser_router
from server.router.client import router as client_router
from server.router.profile import router as profile_router


def configure_router(app: FastAPI, prefix='/api'):
    app.include_router(browser_router, prefix=prefix)
    app.include_router(client_router, prefix=prefix)
    app.include_router(profile_router, prefix=prefix)

def configure_middlewares(app: FastAPI):
    # CORS
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],  # TODO: 這裡要改成正式環境的網址
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
