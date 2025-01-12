from app.database.models import async_session, User, Admin, Task, Reminder
from app.scheduler import scheduler

from sqlalchemy import select, delete, update
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



# tasks

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


async def complete_task(task_id: int, user_id: int):
    async with async_session() as session:
        await session.execute(delete(Task).where(Task.id == task_id))

        await session.execute(
            update(User)
            .where(User.tg_id == user_id)
            .values(
                total_tasks=User.total_tasks + 1,
                monthly_tasks=User.monthly_tasks + 1
            )
        )
        await session.commit()


async def get_completed_tasks(user_id):
    async with async_session() as session:
        result = await session.execute(select(User.total_tasks, User.monthly_tasks).where(User.tg_id == user_id))
        return result.fetchall()[0]


async def clear_monthly(user_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == user_id).values(monthly_tasks = 0))
        await session.commit()


async def get_tasks(user_id):
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.tg_id == user_id).order_by(Task.time))
        tasks = [(task.name, task.time, task.id) for task in result.scalars()]
        return tasks


async def get_times():
    async with async_session() as session:
        result = await session.execute(select(Task.tg_id, Task.time, Task.name))
        return result.all()


async def edit_task_name(task_id, new_name):
    async with async_session() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(name = new_name))
        await session.execute(update(Reminder).where(Task.id == task_id).values(name = new_name))
        await session.commit()


async def edit_task_time(task_id, hours: int, minutes: int):
    async with async_session() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(time = time(hours, minutes)))
        await session.execute(update(Reminder).where(Reminder.task_id == task_id).values(time = time(hours, minutes)))
        await session.commit()
    job = scheduler.get_job(str(task_id))
    job.reschedule(trigger='cron', hour=hours, minute=minutes)

    

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


async def get_reminder_by_id(task_id):
    async with async_session() as session:
        reminder = await session.execute(
            select(Reminder).where(Reminder.task_id == task_id)
        )
        return reminder.scalar_one_or_none()
