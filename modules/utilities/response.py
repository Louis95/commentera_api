"""Potential responses from path operations"""
from modules.database.schemas import message_schemas

base_responses = {
    400: {"model": message_schemas.Message, "description": "Bad request"},
    401: {"model": message_schemas.Message, "description": "Unauthorized"},
    403: {"model": message_schemas.Message, "description": "Forbidden"},
    404: {"model": message_schemas.Message, "description": "Resource Not Found"},
    500: {"model": message_schemas.Message, "description": "Internal Server Error"},
}
