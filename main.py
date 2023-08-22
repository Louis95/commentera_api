"""Main file"""
import os
import sys

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from modules.routers import auth, user
from modules.utilities.auth import CUSTOMER_CONFIG
from modules.utilities.response import base_responses

ENVIRONMENT = os.getenv("RUN_ENV", "local")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
API_TITLE = "Commentera API"


app = FastAPI(
    responses={**base_responses},
    title=API_TITLE,
    description="Commentera offers their customers to create communities, where many "
    "users could comment on articles, created by customers as the community owners",
    docs_url=None,
    openapi_url="/api/v1/openapi.json",
    redoc_url="/docs",
    version="1.0",
)
app.include_router(user.router)
app.include_router(auth.router)


@app.on_event("startup")
async def startup_event():
    """Startup event to update customer configurations"""
    print("Starting event to refresh customer configuration..")
    await CUSTOMER_CONFIG.start_refresh_task()


if __name__ == "__main__":
    load_dotenv()
    if "DATABASE_URL" in os.environ:
        # CUSTOMER_CONFIG.start_refresh_task()  # Start the refresh task
        api_host = os.getenv("API_HOST", "0.0.0.0")
        api_port = int(os.getenv("API_PORT", "8000"))
        if ENVIRONMENT == "local":
            uvicorn.run(
                "main:app",
                host=api_host,
                port=api_port,
                reload=True,
            )
        else:
            uvicorn.run(app, host=api_host, port=api_port)
    else:
        sys.stderr.write(
            "Variable DATABASE_URL cannot be found in environment. Put it in .env or in "
            "the DATABASE_URL environment variable\n",
        )
