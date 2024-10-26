from pydantic import BaseModel, EmailStr

class VerificationRequest(BaseModel):
    user_id: int
    code: str


class SuccessVerification(BaseModel):
    message: str
    user_id: int


class SendVerificationSuccess(BaseModel):
    message: str
    email: EmailStr


class RequestChangePassword(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    new_password: str
    confirm_password: str
    user_id: int


class ChangePasswordInAccount(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
    user_id: int

class RegisterSuccess(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str


class RegisterResponse(BaseModel):
    message: str
    user: RegisterSuccess


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class UpdateProfile(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    user_id: int