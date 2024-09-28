from os import getenv


class Config:
    MOCK_ENDPOINT = getenv('MOCK_ENDPOINT')
    MOCK_PASSWORD = getenv('MOCK_PASSWORD')