from apscheduler.schedulers.asyncio import AsyncIOScheduler
import app.database.requests as rq

scheduler = AsyncIOScheduler()

async def send_sheduled_message(bot, chat_id, tasks_name, task_time):
    await bot.send_message(chat_id=chat_id, text=f'{str(task_time)[:5]}! \n{tasks_name}')

async def restore_jobs(bot):
    reminders = await rq.get_reminders()

    for reminder in reminders:
        scheduler.add_job(
            send_sheduled_message,
            'cron',
            hour=reminder.time.hour,
            minute=reminder.time.minute,
            args=[bot, reminder.tg_id, reminder.name, reminder.time],
            id=str(reminder.task_id)  # Устанавливаем ID напоминания
        )
