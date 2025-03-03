import asyncpg
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

class DBConn:
    def __init__(self):
        load_dotenv()
        self.db_pool = None

    async def start_connection(self):
        self.db_pool = await asyncpg.create_pool(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
        )
        print("Connected to database")

    async def close_connection(self):
        await self.db_pool.close()
        print("Closed connection to database")

    async def get_connection(self):
        if self.db_pool is None:
            await self.start_connection()
        return self.db_pool

    @asynccontextmanager
    async def connection(self):
        """Context manager for database connections."""
        if self.db_pool is None:
            await self.start_connection()
        
        # Get a connection from the pool
        conn = await self.db_pool.acquire()
        try:
            yield conn
        finally:
            # Release the connection back to the pool
            await self.db_pool.release(conn)

db_conn = DBConn()