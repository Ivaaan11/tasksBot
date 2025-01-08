import app.keyboards as k
import app.database.requests as rq
from app.scheduler import scheduler, send_sheduled_message
from bot import bot

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()



# starting the bot

@router.message(Command('start'))
async def cmd_start(message: Message):
    await rq.add_new_user(message.from_user.id, message.from_user.username)
    await message.answer(f'Hello {message.from_user.first_name}!')
    await message.answer('Welcome to the Tasks bot!', reply_markup=k.menu_kb())


@router.message(Command('menu'))
async def cmd_menu(message: Message):
    await message.answer('Main menu:', reply_markup=k.menu_kb())



# add task

class TaskForm(StatesGroup):
    name = State()
    time = State()


@router.message(Command('add'))
async def task_enter_name(message: Message, state: FSMContext):
    await message.answer('Enter a name for the task \n e.g. Feed the dog')
    await state.set_state(TaskForm.name)


@router.message(TaskForm.name)
async def task_enter_time(message: Message, state: FSMContext):
    tasks = await rq.get_tasks(message.from_user.id)
    names = [task[0] for task in tasks]

    if message.text in names:
        await message.answer('This task already exists \nTry another name')
        return

    await state.update_data(name = message.text)
    await message.answer('Enter a time for the task \n e.g 12 30')
    await state.set_state(TaskForm.time)


@router.message(TaskForm.time)
async def task_confirm(message: Message, state: FSMContext):
    await state.update_data(time = message.text)
    task = await state.get_data()

    await message.answer(f'New task: \n name: {task['name']} \n time: {task['time']}', reply_markup=k.yes_no_kb())


@router.callback_query(TaskForm.time, F.data == 'no')
async def task_wrong(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Task addition canceled')
    await state.clear()


@router.callback_query(TaskForm.time, F.data == 'yes')
async def task_correct(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    task = await state.get_data()
    hours, minutes = task['time'].split(' ')

    task_id = await rq.add_task(
        name=task['name'],
        task_time=task['time'],
        user_id=callback.from_user.id
    )

    if not task_id:
        await callback.message.answer('Error')
        return

    scheduler.add_job(
        send_sheduled_message,
        'cron',
        hour=hours,
        minute=minutes,
        args=[bot, callback.from_user.id, task['name'], task['time']],
        id=str(task_id)
    )
    await rq.add_reminder(task_id=task_id, tg_id=callback.from_user.id, name=task['name'], task_time=task['time'])

    await callback.message.answer('Task added \nSee your tasks: /tasks')
    await state.clear()



# show tasks

@router.message(Command('tasks'))
async def cmd_tasks(message: Message):
    tasks = await rq.get_tasks(message.from_user.id)

    answer = ''
    i = 1
    for task in tasks:
        answer = f'''{answer}
{i}. {task[0]}
    {str(task[1])[:5]}
'''
        i += 1
    
    if answer:
        await message.answer(f'Your tasks: \n{answer} \nTo delete a task /delete \nTo add a new task /add')
    else:
        await message.answer('You have no tasks')



# deleting tasks

class DeleteTask(StatesGroup):
    task_id = State()


@router.message(Command('delete'))
async def cmd_delete(message: Message, state: FSMContext):
    if not await rq.get_tasks(message.from_user.id):
        await message.answer('You have no tasks')
        return

    await state.set_state(DeleteTask.task_id)

    await message.answer('Select a task to delete:', reply_markup=await k.task_list_kb(message.from_user.id))


@router.callback_query(DeleteTask.task_id)
async def deleting_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == 'cancel_deleting':
        await callback.message.answer('Action canceled')
        await state.clear()
        return

    await state.update_data(task_id = callback.data)
    task_to_delete = await rq.get_task_by_id(callback.data)
    task_id = task_to_delete[2]

    if scheduler.get_job(task_id):
        scheduler.remove_job(task_id)
    
    await rq.delete_reminder(task_id)
    await rq.delete_task(task_id)

    await callback.message.answer(f'Task <b>{task_id}</b> has been deleted', parse_mode='HTML')
    await state.clear()



# echo callback

@router.callback_query(F.data == 'yes')
async def echo_yes(callback: CallbackQuery):
    await callback.answer()

@router.callback_query(F.data == 'no')
async def echo_no(callback: CallbackQuery):
    await callback.answer()
