import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Missing environment variable: {var_name}")
    return value


db_name = get_env_variable("DATABASE_NAME")
db_user = get_env_variable("DATABASE_USERNAME")
db_password = get_env_variable("DATABASE_PASSWORD")
db_host = get_env_variable("DATABASE_HOST")
algorithm = get_env_variable("ALGORITHM")
secret_token = get_env_variable("SECRET_KEY")
zone_upload_path = get_env_variable("ZONE_UPLOAD_DIRECTORY")
profile_upload_path = get_env_variable("PROFILE_UPLOAD_DIRECTORY")


try:
    expiration_token = int(get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
except ValueError:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer")

DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"

SECRET_KEY = secret_token
ALGORITHM = algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = expiration_token
ZONE_UPLOAD_DIRECTORY = zone_upload_path
PROFILE_UPLOAD_DIRECTORY = profile_upload_path
