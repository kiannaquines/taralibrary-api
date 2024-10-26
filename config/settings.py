import os
from dotenv import load_dotenv
from urllib.parse import quote
load_dotenv()


def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Missing environment variable: {var_name}")
    return value


db_name = get_env_variable("DATABASE_NAME")
db_user = get_env_variable("DATABASE_USERNAME")
db_password = quote(get_env_variable("DATABASE_PASSWORD"))
db_host = get_env_variable("DATABASE_HOST")

try:
    expiration_token = int(get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
except ValueError:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer")

DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"

SECRET_KEY = get_env_variable("SECRET_KEY")
ALGORITHM = get_env_variable("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = expiration_token
ZONE_UPLOAD_DIRECTORY = get_env_variable("ZONE_UPLOAD_DIRECTORY")
PROFILE_UPLOAD_DIRECTORY = get_env_variable("PROFILE_UPLOAD_DIRECTORY")
SMTP_SERVER = get_env_variable("SMTP_SERVER")
SMTP_USERNAME = get_env_variable("SMTP_USERNAME")
SMTP_PASSWORD = get_env_variable("SMTP_PASSWORD")
SMTP_PORT = get_env_variable("SMTP_PORT")

DIR_UPLOAD_ZONE_IMG = ZONE_UPLOAD_DIRECTORY.split('/')[1]
DIR_UPLOAD_PROFILE_IMG = PROFILE_UPLOAD_DIRECTORY.split('/')[1]

