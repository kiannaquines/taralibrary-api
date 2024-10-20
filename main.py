from fastapi import FastAPI, HTTPException, Depends
from markupsafe import Markup
from config.settings import SECRET_KEY
from routes.auth_route import auth_router
from routes.zone_route import zone_router
from database.models import (
    Base,
    User,
    Zones,
    Comment,
    Device,
    VerificationCode,
    Prediction,
    Category,
    ZoneImage,
)
from services.db_services import engine, get_db
from routes.comment_route import comment_router
from routes.prediction_route import prediction_router
from routes.users_route import users_router
from routes.websocket_routes import websocket_router
from routes.device_route import device_router
from routes.chart_routes import charts_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes.category_routes import category_router
from starlette_admin.contrib.sqla import Admin, ModelView
from fastapi.staticfiles import StaticFiles
from starlette_admin.contrib.sqla import Admin
from starlette.middleware.sessions import SessionMiddleware
from provider.auth_provider import CustomAuthProvider

Base.metadata.create_all(bind=engine)

origins = ["*"]

app = FastAPI(
    title="Crowd Monitoring System API",
    description="A crowd monitoring system API for managing crowd data and analyzing patterns.",
    version="1.0.0",
)

app.mount(
    "/static",
    app=StaticFiles(directory="static", packages=["starlette_admin"]),
    name="static",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

auth_provider = CustomAuthProvider(next(get_db()))


class ZoneImageModelView(ModelView):
    def format_value(self, model, attribute):
        if attribute == "image_url" and getattr(model, attribute):
            image_url = getattr(model, attribute)
            return Markup(f'<img src="/static/zone/{image_url}" style="max-width: 100px; max-height: 100px;">')
        return super().format_value(model, attribute)
    
    def scaffold_list_columns(self):
        return ['id', 'image_preview', 'image_url', 'zone_id']
    
    def image_preview(self, model):
        return Markup(f'<img src="/static/zone/{model.image_url}" style="max-width: 100px; max-height: 100px;">')


admin = Admin(engine, title="Crowd Monitoring Admin", auth_provider=auth_provider)
admin.add_view(ModelView(User, name="Users", label="Users", icon="fas fa-user"))
admin.add_view(ModelView(Zones, name="Sections", label="Sections", icon="fas fa-map"))
admin.add_view(ModelView(VerificationCode, name="Verification Code", icon="fas fa-key"))
admin.add_view(ZoneImageModelView(ZoneImage, name="Zone Images", icon="fas fa-image"))
admin.add_view(ModelView(Comment, name="Comments", icon="fas fa-comment"))
admin.add_view(ModelView(Device, name="Devices", icon="fas fa-mobile"))
admin.add_view(ModelView(Prediction, name="Predictions", icon="fas fa-chart-line"))
admin.add_view(
    ModelView(Category, name="Categories", label="Categories", icon="fas fa-tags")
)
admin.mount_to(app)

app.include_router(websocket_router, prefix="/api/v1", tags=["WebSockets"])
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(zone_router, prefix="/api/v1", tags=["Zones"])
app.include_router(comment_router, prefix="/api/v1", tags=["Comment"])
app.include_router(device_router, prefix="/api/v1", tags=["Devices"])
app.include_router(prediction_router, prefix="/api/v1", tags=["Predictions"])
app.include_router(charts_router, prefix="/api/v1", tags=["Charts"])
app.include_router(category_router, prefix="/api/v1", tags=["Category"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])

