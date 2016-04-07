import uuid


def create_token():
    return uuid.uuid4().hex
