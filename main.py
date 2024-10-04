from fastapi import FastAPI
from routes.auth_route import auth_router
from routes.profile_route import profile_router
from routes.zone_route import zone_router
from database.database import Base
from services.db_services import engine
from routes.likes_route import likes_router
from routes.comment_route import comment_router
from fastapi.middleware.cors import CORSMiddleware

origin = ["*"]

app = FastAPI(
    title="Crowd Monitoring System API",
    description="A crowd monitoring system API for managing crowd data and analyzing patterns.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(profile_router, prefix="/api/v1", tags=["Profiles"])
app.include_router(zone_router, prefix="/api/v1", tags=["Zones"])
app.include_router(likes_router, prefix="/api/v1", tags=["Likes"])
app.include_router(comment_router, prefix="/api/v1", tags=["Comment"])

