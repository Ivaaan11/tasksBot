from app.database.models import async_session, User, Admin, Task, Reminder

from sqlalchemy import select, delete
from datetime import time


async def add_new_user(tg_id, username):
    async with async_session() as session:
        user = await session.scalar(select(User.tg_id).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id = tg_id, username = username))
            await session.commit()


async def get_admins():
    async with async_session() as session:
        return await session.execute(select(Admin))


async def add_task(name, task_time, user_id):
    hours, minutes = map(int, task_time.split(' '))

    async with async_session() as session:
        new_task = Task(
            name = name,
            time = time(hours, minutes),
            tg_id=user_id
        )
        session.add(new_task)
        await session.flush()
        task_id = new_task.id
        await session.commit()
        return task_id


async def delete_task(task_id: int):
    async with async_session() as session:
        await session.execute(delete(Task).where(Task.id == task_id))
        await session.commit()
    

async def get_tasks(user_id):
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.tg_id == user_id).order_by(Task.time))
        tasks = [(task.name, task.time, task.id) for task in result.scalars()]
        return tasks


async def get_task_by_id(task_id):
    async with async_session() as session:
        result = await session.scalar(select(Task).where(Task.id == task_id))
        task = (result.name, result.time, result.id)

        return task


async def get_times():
    async with async_session() as session:
        result = await session.execute(select(Task.tg_id, Task.time, Task.name))
        return result.all()
    


# reminders

async def add_reminder(task_id, tg_id, name, task_time):
    hours, minutes = map(int, task_time.split(' '))
    async with async_session() as session:
        new_reminder = Reminder(
            task_id=task_id,
            tg_id=tg_id,
            name=name,
            time=time(hours, minutes)
        )
        session.add(new_reminder)
        await session.commit()


async def delete_reminder(task_id: int):
    async with async_session() as session:
        await session.execute(delete(Reminder).where(Reminder.task_id == task_id))
        await session.commit()


async def get_reminders():
    async with async_session() as session:
        result = await session.execute(select(Reminder))
        return result.scalars().all()

