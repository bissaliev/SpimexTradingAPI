from fastapi import FastAPI

from api.routers.tradings import router as trading_router

app = FastAPI(title="Spimex Trading API")


app.include_router(trading_router, prefix="/trading", tags=["Trading"])
