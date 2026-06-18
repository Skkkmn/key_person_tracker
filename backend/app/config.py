import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'key-person-mgmt-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:wang97976@localhost:3306/key_person_mgmt?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_HOURS = 24
    JWT_REMEMBER_HOURS = 168
