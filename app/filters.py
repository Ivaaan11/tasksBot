from aiogram.types import Message
from aiogram.filters import BaseFilter

import app.database.requests as rq


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        db_admins = await rq.get_admins()
        admin_ids = []

        for admin in db_admins.scalars():
            admin_ids.append(admin.tg_id)
        
        return message.from_user.id in admin_ids
