from fastapi import FastAPI
from routes.auth_route import auth_router
from routes.zone_route import zone_router
from database.models import Base
from services.db_services import engine
from routes.comment_route import comment_router
from routes.prediction_route import prediction_router
from routes.users_route import users_router
from routes.websocket_routes import websocket_router
from routes.device_route import device_router
from routes.chart_routes import charts_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes.category_routes import category_router
from fastapi.staticfiles import StaticFiles
from routes.generate_route import generate_report_router

Base.metadata.create_all(bind=engine)

origins = ["*"]

app = FastAPI(
    title="Crowd Monitoring System API",
    description="A crowd monitoring system API for managing crowd data and analyzing patterns.",
    version="1.0.0",
)

app.mount(
    "/static",
    app=StaticFiles(directory="static"),
    name="static",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_report_router, prefix="/api/v1", tags=["Reports"])
app.include_router(websocket_router, prefix="/api/v1", tags=["WebSockets"])
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(zone_router, prefix="/api/v1", tags=["Zones"])
app.include_router(comment_router, prefix="/api/v1", tags=["Comment"])
app.include_router(device_router, prefix="/api/v1", tags=["Devices"])
app.include_router(prediction_router, prefix="/api/v1", tags=["Predictions"])
app.include_router(charts_router, prefix="/api/v1", tags=["Charts"])
app.include_router(category_router, prefix="/api/v1", tags=["Category"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
