from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_password_hash, ApiKeyEncryption, generate_random_key, generate_hash_key
from src.celery_tasks import send_email
from src.db.models import User, ApiKey


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        result = await session.exec(select(User).where(User.email == email))

        return result.first()

    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)
        password = generate_random_key()
        api_key = generate_random_key()
        print(api_key)
        print("=======================")
        print(password)

        new_user.password_hash = generate_password_hash(password)

        session.add(new_user)
        await session.flush()

        session.add(ApiKey(key=ApiKeyEncryption().encrypt_data(api_key),
                           hashed_key=generate_hash_key(api_key),
                           user_id=new_user.id))

        await session.commit()
        html = f"""
                <h1>Welcome to ABC Library</h1>
                <p> Please find below the credentials<p>
                <p> Temporary Password: {password}<p> You can change once logged in
                <p> API Key: {api_key}<p>
                """

        emails = [new_user.email]

        subject = "Welcome to ABC Library"

        send_email.delay(emails, subject, html)

        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()

        return user
