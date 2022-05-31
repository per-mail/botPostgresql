import logging
import config
import filters

from aiogram import Bot, Dispatcher, executor, types
from filters import IsAdminFilter

import psycopg2
import json, string

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message


# log
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)



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
             """CREATE TABLE IF NOT EXISTS spisok (
                user_id serial PRIMARY KEY,
                block  integer NOT NULL);"""
        )
         
db_object = connection.cursor()

@dp.message_handler(commands='start')
async def start(message: types.Message):    
    await message.answer('Выберите категорию')

#подключение к базе
    user_id = message.from_user.id
    username = message.from_user.username
    db_object.execute(f"SELECT user_id FROM spisok WHERE user_id = {message.from_user.id}")
    result = db_object.fetchone()
    print(result)
    db_object.execute(f"UPDATE spisok SET block = 1 WHERE user_id = {message.from_user.id}")
    if result == None:        
         db_object.execute("INSERT INTO spisok (user_id, block) VALUES (%s,%s)", (message.from_user.id, 0))
         
        
    db_object.execute(f"SELECT block FROM spisok WHERE user_id = {message.from_user.id}")
    result = db_object.fetchone()           
    print(result)           
    
    a = result[0]    # здесь мы извлекаем 1 или 0 из 1, или 0, которая приходит из базы   
    if a == 1:
        await message.answer('OK')
    else:
        await message.answer('DOK')
         
    
        
        




if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
