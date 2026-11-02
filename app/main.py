from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, summary=settings.APP_SUMMARY)


@app.get("/health", tags=["Health check"])
def get_app_status():
    return {"Status": "Alive"}
