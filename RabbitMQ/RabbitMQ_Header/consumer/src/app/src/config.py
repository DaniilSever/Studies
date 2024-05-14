class Config:
    RABBITMQ_USER = "rmuser"
    RABBITMQ_PASSWORD = "rmpassword"
    RABBITMQ_HOST = "215.21.0.54"
    RABBITMQ_PORT = 5672
    RABBITMQ_VHOST = "/"

def get_config():
    return Config()