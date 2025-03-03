from models.user import UserCreate, User, UserWithPassword, UserRole
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
                
                roles = row["roles"] if "roles" in row else [UserRole.USER]
                
                if include_password:
                    user = UserWithPassword(
                        id=row["id"],
                        email=row["email"],
                        username=row["username"],
                        hashed_password=row["password"],
                        roles=roles,
                    )
                else:
                    user = User(
                        id=row["id"],
                        email=row["email"],
                        username=row["username"],
                        roles=roles,
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
        
    async def add_role_to_user(self, user_id: int, role: UserRole) -> None:
        """
        Add a role to a user

        Args:
            user_id: User ID
            role: Role to add
        """

        query = """
        UPDATE users
        SET roles = array_append(roles, $2)
        WHERE id = $1;
        """
        try:
            async with db_conn.connection() as connection:
                await connection.execute(query, user_id, role)
        except Exception as e:
            raise DatabaseError(f"Error adding role to user: {str(e)}")
        
    async def remove_role_from_user(self, user_id: int, role: UserRole) -> None:
        """
        Remove a role from a user

        Args:
            user_id: User ID
            role: Role to remove
        """

        query = """
        UPDATE users
        SET roles = array_remove(roles, $2)
        WHERE id = $1;
        """
        try:
            async with db_conn.connection() as connection:
                await connection.execute(query, user_id, role)
        except Exception as e:
            raise DatabaseError(f"Error removing role from user: {str(e)})")

userdb = UserDB()