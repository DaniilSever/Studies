class Config:
    RABBITMQ_USER = "rmuser"
    RABBITMQ_PASSWORD = "rmpassword"
    RABBITMQ_HOST = "rabbitmq"
    RABBITMQ_PORT = 5672
    RABBITMQ_VHOST = "/"


def get_config():
    return Config()
