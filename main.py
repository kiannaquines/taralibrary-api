from fastapi import FastAPI
from routes.auth_route import auth_router
from routes.profile_route import profile_router
from routes.zone_route import zone_router
from routes.zone_img_route import zone_img_router
from database import Base
from services.db_services import engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(profile_router, prefix="/api/v1", tags=["profiles"])
app.include_router(zone_router, prefix="/api/v1", tags=["zones"])
app.include_router(zone_img_router, prefix="/api/v1", tags=["zone-images"])