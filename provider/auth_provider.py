from fastapi import Depends, HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from sqlalchemy.orm import Session
from starlette_admin.auth import AuthProvider

from database.models import User
from services.auth_services import verify_password
from services.db_services import get_db

class CustomAuthProvider(AuthProvider):
    def __init__(self, db: Session):
        self.db = db
        self.login_path: str = "/login"
        self.logout_path: str = "/logout"
        self.allow_routes: list[str] = [self.login_path, "/static"]
        self.allow_paths: list[str] = self.allow_routes

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 3:
            raise HTTPException(
                status_code=400, detail="Username must be at least 3 characters"
            )

        user = self.db.query(User).filter(User.username == username).first()

        if user and verify_password(password, user.hashed_password):
            request.session.update({"username": username})
            return response

        raise HTTPException(status_code=401, detail="Invalid username or password")

    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("username") is not None:
            username = request.session["username"]
            user = self.db.query(User).filter(User.username == username).first()
            if user:
                request.state.user = user
                return True

        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user = request.state.user
        custom_app_title = f"Hello, {user.username}!"
        custom_logo_url = None

        return AdminConfig(
            app_title=custom_app_title,
            logo_url=custom_logo_url,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        return AdminUser(username=user.username)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
    
def get_auth_provider(db: Session = Depends(get_db)) -> CustomAuthProvider:
    return CustomAuthProvider(db)