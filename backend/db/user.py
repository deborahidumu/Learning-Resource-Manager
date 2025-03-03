from models.user import UserCreate, User, UserWithPassword
from core.security import get_password_hash
from core.exceptions import UserExistsError, DatabaseError
from .conn import db_conn

class UserDB:
    async def get_user(self, identifier: str, include_password: bool = False) -> User:
        """
        Get user by email or username

        Args:
            identifier: Email or username
            include_password: Whether to include the password in the response

        Returns:
            User or UserWithPassword object if found, None if not found
        """

        query = """
        SELECT * FROM users
        WHERE email = $1 OR username = $1;
        """
        try:
            async with db_conn.connection() as connection:
                row = await connection.fetchrow(query, identifier)
                if not row:
                    return None
                
                if include_password:
                    user = UserWithPassword(
                        id=row["id"],
                        email=row["email"],
                        username=row["username"],
                        hashed_password=row["password"],
                    )
                else:
                    user = User(
                        id=row["id"],
                        email=row["email"],
                        username=row["username"],
                    )
                return user
        except Exception as e:
            raise DatabaseError(f"Error retrieving user: {str(e)}")
        
    async def authenticate_user(self, identifier: str) -> User:
        """
        Get a user by email or username, with password for authentication purposes

        Args:
            identifier: Email or username

        Returns:
            UserWithPassword object if found, None if not found
        """
        return await self.get_user(identifier, include_password=True)

    async def create_user(self, user: UserCreate) -> int:
        """
        Create a new user in the database

        Args:
            user: User data object with email, username, and password

        Returns:
            ID of the newly created
        """
        try:
            user_exists = await self.get_user(user.email)

            if user_exists:
                raise UserExistsError(f"User with email {user.email} already exists")

            hashed_password = get_password_hash(user.password)

            query = """
            INSERT INTO users (email, username, password)
            VALUES ($1, $2, $3)
            RETURNING id;
            """

            # Use the updated connection manager
            async with db_conn.connection() as connection:
                user_id = await connection.fetchval(query, user.email, user.username, hashed_password)
                return user_id
        except UserExistsError:
            # Re-raise user exists errors
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to create user: {str(e)}")

userdb = UserDB()