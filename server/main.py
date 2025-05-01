from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database and models
from database import engine, Base

# Import routes
from routes.stock import stock_router
from routes.auth import auth_router
from routes.user_stock import user_stock_router 
from routes.ai_routes import ai_router
from routes.trades import trades_router
from routes.user import user_router
from routes.strategy import strategy_router
from routes.automation import automation_router

# Import scheduler
from scheduler import start_scheduler

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_router) 
app.include_router(auth_router)
app.include_router(user_stock_router)
app.include_router(ai_router)
app.include_router(trades_router)
app.include_router(user_router)
app.include_router(strategy_router)
app.include_router(automation_router)

# Запуск фонового планировщика
@app.on_event("startup")
async def startup_event():
    start_scheduler()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)