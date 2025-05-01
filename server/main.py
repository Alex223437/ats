from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database and models
from server.database import engine, Base

# Import routes
from server.routes.stock import stock_router
from server.routes.auth import auth_router
from server.routes.user_stock import user_stock_router 
from server.routes.ai_routes import ai_router
from server.routes.trades import trades_router
from server.routes.user import user_router
from server.routes.strategy import strategy_router
from server.routes.automation import automation_router

# Import scheduler
from server.scheduler import start_scheduler

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