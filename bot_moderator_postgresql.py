import logging
import config
import filters

from aiogram import Bot, Dispatcher, executor, types
from filters import IsAdminFilter

import psycopg2
import json, string
from aiogram.types import Message


from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message

# log
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)





logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
dp.filters_factory.bind(IsAdminFilter)

host = "ec2-54-170-212-187.eu-west-1.compute.amazonaws.com"
user = "wqqpnpyynsqusp"
password = "8a0437465e59162be7987a46fffe5bd66fc47a5a894e28b128cca83655bf29e7"
db_name = "d3aihcljr5saeo"


# connect to exist database соединяемся с сервером и получаем версию сервера
connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name    
)
connection.autocommit = True 

with connection.cursor() as cursor:
         cursor.execute(
             """CREATE TABLE IF NOT EXISTS spisok(
                user_id BIGSERIAL PRIMARY KEY,
                block  BIGINT NOT NULL);"""
        )
         
db_object = connection.cursor()


class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()

# функция оповещение о старте
async def on_startup(_):
    print('Админ следит за чатом!')


@dp.message_handler(commands=['start'])
async def start(message: Message):
    if message.from_user.id == config.ADMIN:        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        await bot.send_message(message.from_user.id, 'Добро пожаловать в Админ-Панель! Выберите действие на клавиатуре', reply_markup=keyboard)
        
    else:
        if result is None:
            db_object = connection.cursor()
            db_object.execute(f"SELECT * FROM spisok WHERE user_id = {message.from_user.id}")
            rez = db_object.fetchone()
            if rez is None:
                db_object.execute("INSERT INTO spisok (user_id, block) VALUES (%s,%s)", (message.from_user.id, 0))            
            await message.answer('Привет')
        else:
            await message.answer('Ты был заблокирован!')


@dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: Message):
    if message.from_user.id == config.ADMIN:
        await dialog.spam.set()
        await message.answer('Напиши текст рассылки')
    else:
        await message.answer('Вы не являетесь админом')
        

@dp.message_handler(state=dialog.spam)
async def start_spam(message: Message, state: FSMContext):
    if message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        await message.answer('Главное меню', reply_markup=keyboard)
        await state.finish()
    else:
        db_object = connection.cursor()
        db_object.execute(f"SELECT user_id FROM spisok WHERE user_id = {message.from_user.id}")
        spam_base = db_object.fetchall()
        print(spam_base)
        for q in range(len(spam_base)):
            print(spam_base[q][0])
        for q in range(len(spam_base)):
            await bot.send_message(spam_base[q][0], message.text)
        await message.answer('Рассылка завершена')
        await state.finish()


@dp.message_handler(state='*', text='Назад')
async def back(message: Message):
    if message.from_user.id == config.ADMIN:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        await message.answer('Главное меню', reply_markup=keyboard)
    else:
        await message.answer('Вам не доступна эта функция')


@dp.message_handler(content_types=['text'], text='Добавить в ЧС')
async def hanadler(message: types.Message, state: FSMContext):
    if message.chat.id == config.ADMIN:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Назад"))
        await message.answer(
            'Введите id пользователя, которого нужно заблокировать.\nДля отмены нажмите кнопку ниже',
            reply_markup=keyboard)
        await dialog.blacklist.set()


@dp.message_handler(state=dialog.blacklist)
async def proce(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        await message.answer('Отмена! Возвращаю назад.', reply_markup=keyboard)
        await state.finish()
    else:
        if message.text.isdigit():
            db_object = connection.cursor()
            db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.from_user.id}")
            result = db_object.fetchall()            
            if len(result) == 0:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                await message.answer('Такой пользователь не найден в базе данных.', reply_markup=keyboard)
                await state.finish()
            else:
                a = result[0] # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы    
                d = a[0]                
                if d == 0:
                    db_object.execute(f"UPDATE spisok SET block = 1 WHERE user_id = {message.from_user.id}")
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    await message.answer('Пользователь успешно добавлен в ЧС.', reply_markup=keyboard)
                    await state.finish()
                    await bot.send_message(message.text, 'Администратор добавил Вас в чёрный список!')                    
                else:
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    await message.answer('Данный пользователь уже получил бан', reply_markup=keyboard)
                    await state.finish()
        else:
            await message.answer('Ты вводишь буквы...\n\nВведи ID')


@dp.message_handler(content_types=['text'], text='Убрать из ЧС')
async def hfandler(message: types.Message, state: FSMContext):
    if message.chat.id == config. ADMIN:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.InlineKeyboardButton(text="Назад"))
            await message.answer(
                'Введите id пользователя, которого нужно разблокировать.\nДля отмены нажмите кнопку ниже',
                reply_markup=keyboard)
            await dialog.whitelist.set()


@dp.message_handler(state=dialog.whitelist)
async def proc(message: types.Message, state: FSMContext):
    if message.text.isdigit():
            db_object = connection.cursor()
            db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.from_user.id}")
            result = db_object.fetchall()            
            if len(result) == 0:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                await message.answer('Такой пользователь не найден в базе данных.', reply_markup=keyboard)
                await state.finish()
            else:
                a = result[0] # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы    
                d = a[0]
                if d == 1:
                    db_object = connection.cursor()
                    db_object.execute(f"UPDATE spisok SET block = 1 WHERE user_id = {message.from_user.id}")
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    await message.answer('Пользователь успешно разбанен.', reply_markup=keyboard)
                    await state.finish()
                    await bot.send_message(message.text, 'Вы были разблокированы администрацией.')
                else:
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    await message.answer('Данный пользователь не получал бан.', reply_markup=keyboard)
                    await state.finish()
    else:
          await message.answer('Ты вводишь буквы...\n\nВведи ID')
   
    

# приветствие, удаленние записи, внесение в базу, удаление пользователей которые в чёрном списке
@dp.message_handler(content_types=["new_chat_members"])
async def on_user_joined(message: types.Message, state: FSMContext):
    db_object = connection.cursor()
    db_object.execute(f"SELECT * FROM spisok WHERE user_id = {message.from_user.id}")
    rez = db_object.fetchone()
    if rez is None:
        db_object.execute("INSERT INTO spisok (user_id, block) VALUES (%s,%s)", (message.from_user.id, 0))   
    await message.delete()
    db_object = connection.cursor()
    db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.from_user.id}")
    result = db_object.fetchall()           
               
    a = result[0]   # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы            
    d = a[0] 
    if d == 1:
         await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.from_user.id)
         await bot.send_message(message.from_user.id, 'Вы в чёрном списке группы за нарушение правил!')
    else:
         await message.answer('Добро пожаловать в чат\nПредставьтесь пожалуйста!') 
                      
                     
                      


#  удаление
@dp.message_handler(is_admin=True, commands=["weg"], commands_prefix="!/")
async def cmd_ban(message: types.Message, state: FSMContext):
    if not message.reply_to_message:
        await message.reply("Кого нужно удалить?")
        return
    await message.bot.delete_message(config.GROUP_ID, message.message_id)
    await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)
    await message.reply_to_message.reply("Полльзователь удалён")
    await bot.send_message(message.reply_to_message.from_user.id, 'Вас удалили из группы за нарушение правил!') 
    
    db_object = connection.cursor()
    db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.reply_to_message.from_user.id}")
    result = db_object.fetchall()           
               
    a = result[0]  # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы         
    d = a[0]
    if d == 0:
                db_object.execute(f"UPDATE spisok SET block = 1 WHERE user_id = {message.reply_to_message.from_user.id}")                    
                await state.finish()
    

# заносим пользователя в чёрный список в чате
@dp.message_handler(is_admin=True, commands=["ban"], commands_prefix="!/")
async def cmd_ban(message: types.Message, state: FSMContext):
    if not message.reply_to_message:
        await bot.send_message(message.from_user.id, "Кого нужно забанить?")
        await message.bot.delete_message(config.GROUP_ID, message.message_id)
        return
    await message.bot.delete_message(config.GROUP_ID, message.message_id)
    
    
    db_object = connection.cursor()
    db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.reply_to_message.from_user.id}")
    result = db_object.fetchall()
               
    a = result[0]      # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы          
    d = a[0]
    if d == 0:
                db_object = connection.cursor()
                db_object.execute(f"UPDATE spisok SET block = 1 WHERE user_id = {message.reply_to_message.from_user.id}")

                await bot.send_message(message.reply_to_message.from_user.id, 'Администратор добавил Вас в чёрный список!')
                await bot.send_message(message.from_user.id, 'Пользователь забанен.')
                await state.finish()
    else:
                    
                await bot.send_message(message.from_user.id, 'Данный пользователь уже получил бан')
                await state.finish()
                

# убираем пользователя из чёрного списка в чате
@dp.message_handler(is_admin=True, commands=["free"], commands_prefix="!/")
async def cmd_free(message: types.Message, state: FSMContext):
    if not message.reply_to_message:
        await bot.send_message(message.from_user.id, "Кого нужно забанить?")
        await message.bot.delete_message(config.GROUP_ID, message.message_id)
        return
    await message.bot.delete_message(config.GROUP_ID, message.message_id)
    
    
    db_object = connection.cursor()
    db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.reply_to_message.from_user.id}")
    result = db_object.fetchall()    
    
               
    a = result[0]  # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы        
    d = a[0]
    if d == 1:
                db_object = connection.cursor()
                db_object.execute(f"UPDATE spisok SET block = 0 WHERE user_id = {message.reply_to_message.from_user.id}")                    
                await bot.send_message(message.reply_to_message.from_user.id, 'Администратор удалил Вас из чёрного списка!')
                await bot.send_message(message.from_user.id, 'Пользователь удалён из чёрного списка')
                await state.finish()
    else:
                    
                await bot.send_message(message.from_user.id, 'Данный пользователь не получал бан.')
                await state.finish()
              



#  получаем user.id пользователя
@dp.message_handler(is_admin=True, commands=["id"], commands_prefix="!/")
async def cmd_ban(message: types.Message):
    await bot.send_message(message.from_user.id, message.reply_to_message.from_user.id)
    await message.bot.delete_message(config.GROUP_ID, message.message_id)    



#заносим пользователей в базу и фильтруем чат
@dp.message_handler()
async def filter_message(message: types.Message, state: FSMContext):
    db_object = connection.cursor()
    db_object.execute(f"SELECT * FROM spisok WHERE user_id = {message.from_user.id}")
    rez = db_object.fetchone()
    if rez is None:
        db_object.execute("INSERT INTO spisok (user_id, block) VALUES (%s,%s)", (message.from_user.id, 0))
    
       
    for i in (".рф", ".ru", ".com", '.biz'):
        if i in message.text.lower():
            await message.delete()                 
            
            db_object = connection.cursor()
            db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.from_user.id}")
            result = db_object.fetchall()           
               
            a = result[0]   # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы         
            d = a[0]
            if d == 0:
                       db_object.execute(f"UPDATE spisok SET block = 1 WHERE user_id = {message.from_user.id}")
                       await message.answer('Пользователь успешно добавлен в ЧС.')
                       await state.finish()
                       await bot.send_message(message.from_user.id, 'Первое предупреждение!')   
            
            if d == 1:                            
                      await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.from_user.id)
                      await bot.send_message(message.from_user.id, 'Вас удалили из группы за нарушение правил!') 
                      await message.answer("Пользователь удалён")
             
            
#видео о фильтре мата https://www.youtube.com/watch?v=Lgm7pxlr7F0&list=PLNi5HdK6QEmX1OpHj0wvf8Z28NYoV5sBJ&index=3            
    if {i.lower().translate(str.maketrans('','',string.punctuation)) for i in message.text.split(' ')}\
       .intersection(set(json.load(open('spisok.json')))) != set():
       await message.delete()
       db_object = connection.cursor()
       db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.from_user.id}")
       result = db_object.fetchall()           
               
       a = result[0]        # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы         
           
       d = a[0]
       if d == 0:
                      db_object.execute(f"UPDATE spisok SET block = 1 WHERE user_id = {message.from_user.id}")                  
                      await message.answer('Пользователь успешно добавлен в ЧС.')
                      await state.finish()
                      await bot.send_message(message.from_user.id, 'Первое предупреждение!')   
            
       if d == 1:                            
                      await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.from_user.id)
                      await bot.send_message(message.from_user.id, 'Вас удалили из группы за нарушение правил!') 
                      await message.answer("Пользователь удалён")
             

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
