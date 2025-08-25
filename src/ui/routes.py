from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()


def get_templates() -> Jinja2Templates:
    from src.main import templates

    return templates


@router.get("/", response_class=HTMLResponse)
async def ui_home(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/about", response_class=HTMLResponse)
async def ui_about(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    return templates.TemplateResponse("about.html", {"request": request})
