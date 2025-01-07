from app.handlers import user, admin, payments
from app.database.models import async_main
from app.scheduler import scheduler, restore_jobs

import app.middlewares as middlewares
from bot import bot, dp

import asyncio
import logging

from aiogram.types import BotCommand, BotCommandScopeDefault


commands = [
    BotCommand(command='start', description='Starts the bot'),
    BotCommand(command='menu', description='Shows the main menu'),
    BotCommand(command='cancel', description='Cancels the current state'),
    BotCommand(command='add', description='Adds a new task'),
    BotCommand(command='tasks', description='Shows all the tasks'),
    BotCommand(command='delete', description='Deletes the task with the specified number'),
]

async def main():
    await async_main()

    logging.basicConfig(level=logging.INFO)
    await restore_jobs(bot)
    scheduler.start()

    dp.message.middleware(middlewares.CancelMiddleware())
    dp.include_routers(
        user.router,
        admin.router,
        payments.router
    )
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
