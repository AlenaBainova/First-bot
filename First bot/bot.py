import aiogram
import os
import asyncio
import logging
import pandas as pd
import sys
import io
import button as kb
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputFile
from aiogram.filters import CommandStart
from aiogram.methods.send_document import SendDocument

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
data = None
form_router = Router()

class Form(StatesGroup):
   name = State()

@form_router.message(CommandStart()) 
async def send_welcome(message: Message):
   await message.answer("👋 Добро пожаловать!\n⬇️ Загрузить ваш файл Ecxel.")

@form_router.message(F.document)
async def take_doc(message: Message):
   
   doc = message.document.file_id
   print (doc)
   file = await bot.get_file(doc)
   file_path = file.file_path
   my_object = io.BytesIO()
   
   await message.answer("⌛️ Подождите, файл обрабатывается\n")
      
   MyBinaryIO = await bot.download_file(file_path, my_object)
   global data
   try: # --- Проверка наименования столбцов загруж. файла
      data = pd.read_excel(MyBinaryIO)
      print (data)
      expected_columns = ['Оценка', 'Сокращенная оценка','Период', 'Год','Семестр/Триместр', 'Курс', 'Часть года', 'Уровень контроля', 'Дисциплина', 'Личный номер студента', 'Группа', 'Факультет', 'Программа', 'Форма обучения', 'Тип финансирования']
      column_names = data.columns.tolist()
      if column_names == expected_columns:
         await message.answer(f'✅ Файл успешно загружен!', reply_markup=kb.main1)
      else:
         await message.answer(f'⚠  Файл инвалидный.\nПроверьте наименование, порядок столбцов и загрузите файл ещё раз')
   except Exception as e:
      await message.answer(f"An error occurred: {str(e)}")
     
@form_router.message(F.text == 'Показать список групп')
async def report(message: Message):
   grup = data['Группа'].unique()
   grup_str = ', '.join(grup)
   print(grup_str)
   await message.answer(f'👥 В загруженной базе хранится информация о следующих группах:\n {grup_str}', reply_markup=kb.main2)   

@form_router.message(F.text == 'Выбрать группу')
async def report(message: Message, state: FSMContext) -> None:
   await state.set_state(Form.name)
   await message.answer(
        "⌨ Введите номер группы: ",
        reply_markup=ReplyKeyboardRemove())

@form_router.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
   await state.update_data(name=message.text)
   skore = data['Группа'].str.contains(str(message.text)).sum()
   if skore == 0:
      await message.answer(f'❌ Вы ввели некорректный номер группы.\nВведите номер группы из списка выше.', reply_markup=kb.main2)
   else:
      await message.answer(f'📄 Для вывода отчёта по группе {html.quote(message.text)} нажмите кнопку "Отчет" 👇', reply_markup=kb.report)

@dp.callback_query(F.data == 'otchet')
async def cbquantity(callback: CallbackQuery, state: FSMContext):
   group = await state.get_data()
   records = data.shape[0]
   marks = data['Группа'].str.contains(group['name']).sum()
   group_student = data.loc[data['Группа'] == group['name'],'Личный номер студента'].unique()
   group_student_str = ', '.join(map(str, group_student)) 
   form_control = data['Уровень контроля'].unique()
   form_control_str = ', '.join(map(str, form_control))
   years = data.loc[data['Группа'] == group['name'],'Год'].unique()
   years_str = ', '.join(map(str, years))
   student = len(data[data['Группа'] == group['name']]['Личный номер студента'].unique())
   await callback.message.answer(f'✔️ В исходном датасете содержалось {records} оценок, из них {marks} относятся к указанной группе\n✔️ В датасете находятся оценки {student} студентов со следующими личными номерами: {group_student_str}\n✔️ Используемые формы контроля: {form_control_str}\n✔️ Данные представлены по следующим учебным годам: {years_str}')
   
   await callback.message.answer(f'Чтобы начать занаво введите /start')

async def main():
   bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
   dp.include_router(form_router)
   await dp.start_polling(bot)

if __name__ == '__main__':
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())