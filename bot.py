import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()
TOKEN = "8775537101:AAFer2zcx-fB1kGX3oXZKdlPps8Ats1cc5Y"  # Создай файл .env и напиши туда BOT_TOKEN=твой_токен

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для викторины
class QuizState(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()
    question5 = State()
    finished = State()

# Словарь для хранения результатов пользователей
user_scores = {}

# ---------- ВОПРОСЫ ВИКТОРИНЫ ----------
QUESTIONS = [
    {
        "text": "❓ Вопрос 1/5: Твой идеальный вечер пятницы?",
        "options": [
            ("Встреча с друзьями в баре до утра", 0),
            ("Лечь в 21:00 под одеялко с сериальчиком", 5),
            ("Пойти в гости, но в 22:00 уже думать, как свалить домой", 10)
        ]
    },
    {
        "text": "❓ Вопрос 2/5: Что у тебя болит чаще всего?",
        "options": [
            ("Душа после вчерашнего", 0),
            ("Спина. Просто так. От того, что резко встал", 5),
            ("Поясница. И я знаю, когда будет дождь", 10)
        ]
    },
    {
        "text": "❓ Вопрос 3/5: Твой завтрак в выходной?",
        "options": [
            ("Я не сплю в выходные, тусовка ждет!", 0),
            ("Плотный обед в 14:00, потому что проснулся только что", 5),
            ("В 8 утра с тарелкой овсянки и стаканом кефира", 10)
        ]
    },
    {
        "text": "❓ Вопрос 4/5: Какую музыку ты ставишь в машине?",
        "options": [
            ("Новинки ТикТока и рэп", 0),
            ("Старый добрый русский рок / Европоп 90-х", 5),
            ("Радио 'Дача' или 'Шансон'", 10)
        ]
    },
    {
        "text": "❓ Вопрос 5/5: Что это за предмет?",
        "photo": "https://i.imgur.com/3YqWr9K.jpg",  # Замени на реальную ссылку с дискетой
        "caption": "Ты знаешь, что это за предмет?",
        "options": [
            ("Это иконка 'Сохранить' в Фигме", 0),
            ("Это дискета, на ней песни хранили", 5),
            ("Это 1.44 мегабайта моего детства... эх", 10)
        ]
    }
]

# ---------- РЕЗУЛЬТАТЫ ----------
RESULTS = {
    "young": {
        "title": "🤡 Зумер-недоучка",
        "description": "Ты или очень молод, или ведешь активный образ жизни, который мы, взрослые, называем 'неудачная попытка заработать геморрой'. Иди, почитай новости, пока мы тут ностальгируем.",
        "gif": "https://media.giphy.com/media/3o7abB06u9bNzA8LC8/giphy.gif"  # Замени на свой мем
    },
    "border": {
        "title": "🤔 Пограничник",
        "description": "Ты еще тусуешься, но уже берешь с собой паспорт и аптечку. Можешь выпить, но в 12 ночи тебя тянет спросить: 'А такси еще ходит?'. Твой лучший друг — Газпром и грелка.",
        "gif": "https://media.giphy.com/media/l0HlNQ03J5JxX6lZ6/giphy.gif"
    },
    "skuf": {
        "title": "👑 Легенда ларька, Почетный Скуф",
        "description": "ПОЗДРАВЛЯЕМ! Твой диагноз — 'Взрослая жизнь в терминальной стадии'. Ты пьешь кефир на ночь, радуешься новой кастрюле и считаешь, что молодежь обнаглела. Твой скелет уже просится наружу, но душа все еще хочет пивка. Добро пожаловать в клуб!",
        "gif": "https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif"
    }
}

# Функция создания клавиатуры с вариантами ответов
def get_options_keyboard(options):
    keyboard = []
    for i, (text, _) in enumerate(options):
        keyboard.append([KeyboardButton(text=text)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ---------- КОМАНДА СТАРТ ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Приветственное сообщение
    welcome_text = (
        "👋 *О, свежее мясо!*\n\n"
        "Ты зашел узнать, насколько ты 'того'? Отвечай честно, "
        "тут детектор лжи — твоя седая борода.\n\n"
        "Пройдешь тест — узнаешь свой диагноз! 🤣"
    )
    
    # Кнопка начала
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🍺 ПОГНАЛИ! 🍺")]],
        resize_keyboard=True
    )
    
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=keyboard)

# ---------- НАЧАЛО ВИКТОРИНЫ ----------
@dp.message(F.text == "🍺 ПОГНАЛИ! 🍺")
async def start_quiz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_scores[user_id] = 0
    
    # Отправляем первый вопрос
    q = QUESTIONS[0]
    await message.answer(
        q["text"],
        reply_markup=get_options_keyboard(q["options"])
    )
    await state.set_state(QuizState.question1)

# ---------- ОБРАБОТКА ОТВЕТОВ ----------
@dp.message(QuizState.question1)
async def process_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    answer = message.text
    
    # Находим баллы за ответ
    points = 0
    for option_text, option_points in QUESTIONS[0]["options"]:
        if answer == option_text:
            points = option_points
            break
    
    user_scores[user_id] = user_scores.get(user_id, 0) + points
    
    # Второй вопрос
    q = QUESTIONS[1]
    await message.answer(
        q["text"],
        reply_markup=get_options_keyboard(q["options"])
    )
    await state.set_state(QuizState.question2)

@dp.message(QuizState.question2)
async def process_q2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    answer = message.text
    
    points = 0
    for option_text, option_points in QUESTIONS[1]["options"]:
        if answer == option_text:
            points = option_points
            break
    
    user_scores[user_id] += points
    
    # Третий вопрос
    q = QUESTIONS[2]
    await message.answer(
        q["text"],
        reply_markup=get_options_keyboard(q["options"])
    )
    await state.set_state(QuizState.question3)

@dp.message(QuizState.question3)
async def process_q3(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    answer = message.text
    
    points = 0
    for option_text, option_points in QUESTIONS[2]["options"]:
        if answer == option_text:
            points = option_points
            break
    
    user_scores[user_id] += points
    
    # Четвертый вопрос
    q = QUESTIONS[3]
    await message.answer(
        q["text"],
        reply_markup=get_options_keyboard(q["options"])
    )
    await state.set_state(QuizState.question4)

@dp.message(QuizState.question4)
async def process_q4(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    answer = message.text
    
    points = 0
    for option_text, option_points in QUESTIONS[3]["options"]:
        if answer == option_text:
            points = option_points
            break
    
    user_scores[user_id] += points
    
    # Пятый вопрос (с фото)
    q = QUESTIONS[4]
    
    # Отправляем фото с вопросом
    await message.answer_photo(
        photo=q["photo"],
        caption=q["caption"],
        reply_markup=get_options_keyboard(q["options"])
    )
    await state.set_state(QuizState.question5)

@dp.message(QuizState.question5)
async def process_q5(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    answer = message.text
    
    points = 0
    for option_text, option_points in QUESTIONS[4]["options"]:
        if answer == option_text:
            points = option_points
            break
    
    user_scores[user_id] += points
    
    # Подсчет результата
    total_score = user_scores[user_id]
    
    # Определяем категорию
    if total_score <= 15:
        result = RESULTS["young"]
    elif total_score <= 35:
        result = RESULTS["border"]
    else:
        result = RESULTS["skuf"]
    
    # Финальное сообщение
    final_text = (
        f"🎉 *ТВОЙ РЕЗУЛЬТАТ:*\n\n"
        f"*{result['title']}*\n"
        f"📊 *Очки взрослости:* {total_score}\n\n"
        f"{result['description']}\n\n"
        f"👉 *Пропуск в мир, где не играет спина:*\n"
        f"Отправь этот результат другу, пусть тоже поржет! 🤣"
    )
    
    # Отправляем гифку с результатом
    await message.answer_animation(
        animation=result["gif"],
        caption=final_text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🍺 ПОГНАЛИ! 🍺")]],
            resize_keyboard=True
        )
    )
    
    # Очищаем состояние
    await state.clear()
    
    # Очищаем результат пользователя (по желанию)
    # del user_scores[user_id]

# ---------- ЗАПУСК БОТА ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
