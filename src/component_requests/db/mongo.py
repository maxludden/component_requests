"""The module for the MongoDB database."""

from __future__ import annotations

from os import getenv

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from component_requests.logger import get_console, get_logger

# Load environment variables from .env file
load_dotenv()

console = get_console()
logger = get_logger()
VERBOSE: bool = False

def get_mongo_uri(verbose: bool = VERBOSE) -> str:
    """Get the MongoDB URI from environment variables."""
    uri = getenv("MONGO_URI", "op://Dev/Mongo-AppliedLogix/uri")
    assert uri, "MONGO_URI is not set in environment variables."
    return uri


def get_client(verbose: bool = VERBOSE) -> AsyncIOMotorClient:
    """Get the MongoDB client.

    Args:
        verbose (bool): Whether to print the connection status.

    Returns:
        AsyncIOMotorClient: The MongoDB client.
    """
    console = get_console()
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient(get_mongo_uri())
        if verbose:
            console.log(
                "[i #00ff00]Connected to the[/][b #ffffff]Requests[/] [i #00ff00]database...[/]"
            )
    except Exception as e:
        console.log(f"Failed to connect to the database: {e}")
        raise ConnectionError(f"Failed to connect to the database: {e}")
    return client


def get_requests_db(verbose: bool = VERBOSE) -> AsyncIOMotorDatabase:
    """Get the MongoDB database."""
    client: AsyncIOMotorClient = get_client()
    try:
        db: AsyncIOMotorDatabase = client.get_database(
            getenv("MONGO_DB", "op://Dev/Mongo-AppliedLogix/db")
        )
    except Exception as e:
        raise ConnectionError(f"Failed to connect to the database: {e}")
    return db


def init_db(verbose: bool = VERBOSE) -> None:
    """Initialize the MongoDB database."""
    init_beanie(database=get_requests_db(), document_models=[Request])
    init_beanie(database=get_requests_db(), document_models=[Request])
