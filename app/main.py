from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.api import api_router
from app.routers.views import views_router
from app.templates_config import templates

app = FastAPI(title="TinyLog", version="0.1.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/sw.js", include_in_schema=False)
async def service_worker():
    return FileResponse("app/static/sw.js", media_type="application/javascript")


@app.exception_handler(404)
async def not_found(request: Request, _exc):
    return templates.TemplateResponse(request, "errors/404.html", status_code=404)


app.include_router(api_router)
app.include_router(views_router)
