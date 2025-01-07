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


@router.message(Command('menu'))
async def cmd_menu(message: Message):
    await message.answer('Main menu')



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
    print(scheduler.get_jobs())

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
        await message.answer(f'Your tasks: \n{answer} \nTo delete a task /delete <task number> \nTo add a new task /add')
    else:
        await message.answer('You have no tasks')



# deleting tasks

@router.message(F.text.startswith('/delete'))
async def cmd_delete(message: Message):
    args = message.text.split(' ')

    if len(args) < 2:
        await message.answer('Your request must look like: \n/ delete <task number> \n e.g. /delete 2')
        return
    
    try:
        tasks = await rq.get_tasks(message.from_user.id)
        task_to_delete_number = int(args[1])
        
        if 0 < task_to_delete_number <= len(tasks):
            task_to_delete = tasks[task_to_delete_number - 1]

            if scheduler.get_job(str(task_to_delete[2])):
                scheduler.remove_job(str(task_to_delete[2]))
            
            await rq.delete_reminder(task_to_delete[2])
            await rq.delete_task(task_to_delete[2])

            await message.answer(f'Task <b>{task_to_delete[0]}</b> has been deleted', parse_mode='HTML')
        else:
            await message.answer(f'Task {task_to_delete_number}  not found')

    except ValueError:
        await message.answer('Invalid task number. Please provide a valid number')



# echo callback

@router.callback_query(F.data == 'yes')
async def echo_yes(callback: CallbackQuery):
    await callback.answer()

@router.callback_query(F.data == 'no')
async def echo_no(callback: CallbackQuery):
    await callback.answer()
