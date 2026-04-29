import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
import pymongo

from config import settings

log = logging.getLogger("uvicorn")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    log.info("Connecting to MongoDB Atlas...")
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client[settings.DB_NAME]
    
    # Verify connection
    try:
        await db_instance.client.admin.command('ping')
        log.info("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        log.error(f"Failed to connect to MongoDB Atlas: {e}")
        raise e

    await create_indexes(db_instance.db)

async def close_mongo_connection():
    log.info("Closing MongoDB Atlas connection...")
    if db_instance.client is not None:
        db_instance.client.close()

async def create_indexes(db):
    """Create optimal indexes for querying the drowsiness datasets."""
    log.info("Ensuring database indexes...")
    
    # Drivers: Unique index on email
    await db.drivers.create_index("email", unique=True)
    
    # Sessions: Indices on driver_id and start_time
    await db.sessions.create_index("driver_id")
    await db.sessions.create_index([("start_time", DESCENDING)])
    
    # Events: Indices on session_id, timestamp, and state
    await db.events.create_index([("session_id", ASCENDING), ("timestamp", ASCENDING)])
    await db.events.create_index("state")

    log.info("Indexes confirmed.")

def get_database():
    return db_instance.db
