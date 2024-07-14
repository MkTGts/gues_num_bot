from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
import requests
from random import randint
import json


bot_token = "token bot"  # сюда нужно установить токен бота
ATTEMPTS = 5  # количество попыток
BOT = Bot(bot_token)
dp = Dispatcher()
random_dig = lambda: randint(1, 100)  # ф-ция генерации рандомного числа


users = {}
get_id = requests.get(
    f"https://api.telegram.org/bot{bot_token}/getUpdates"
    ).json()
id = get_id["result"][0]["message"]["from"]["id"]
if id not in users:
    users[id] = {
    "in_game": False,
    "dig": None,
    "attemp": None,
    "tot_game": 0,
    "win": 0
}
user = users[id]


@dp.message(Command(commands=["start"]))
async def command_start(message: Message):
    await message.answer(text="Это игра угадай число.\nЧто бы прочитать правила введи команду /help\n"
                         "Начнем игру? (ответь Да или Нет)")


@dp.message(Command(commands=["help"]))
async def command_help(message: Message):
    await message.answer(text=f"Я загадаю целое цисло от 1 до 100.\nТебе нужно его угадать.\n"
                         "Дается {ATTEMPTS} попытки.\nЧто бы начать напиши go или нажми команду /go")


# команда вывода статистики игрока
@dp.message(Command(commands=["stat"]))
async def command_stat(message: Message):
    await message.answer("Ваша статистика:\n"
                         f"Всего игр: {user['tot_game']}\n"
                         f"Побед: {user['win']}")


# команда остановки игры
@dp.message(Command(commands=['cancel']))
async def command_cancel(message: Message):
    if user["in_game"]:
        user["in_game"] = False
        user["dig"] = None
        user["attemp"] = None   
        await message.answer("Игра остановлена"
                            "Хотите сыграть снова?(да или нет)")
    else:
        await message.answer("Мы и так не играем.\n"
                             "Начать игру?")


# хендлер команды для начала игры
@dp.message(Command(commands=["go"]))
async def command_go(message: Message):
    if not user["in_game"]:
        user["in_game"] = True
        user["dig"] = random_dig()
        user["attemp"] = ATTEMPTS
        await message.answer("Игра началасб\nЯ загадал число.\n""Начинай угадывать. Введи число.")
    else:
        await message.answer("Мы уже играем."
                             "Пока мы в игре я могу реагировать только на целое число и"
                             "комаду /help /cancel /stat")
        

# хендлер ключевых слов для команды запуска игры
@dp.message(F.text.lower().in_(["да", "lf", "давай", "хочу", "go",
                                                             "играть", "игра", "хочу играть"]))
async def key_word_for_command_go(message: Message):
    await command_go(message)
                

# хендлер обрабатывающий отказ пользователя
@dp.message(F.text.lower().in_(["нет", "не", "не хочу", "ytn"]))
async def procces_negative_answer(message: Message):
    if not user["in_game"]:
        await message.answer("Жаль\nЕсли захотите поиграть просто напишите об этом.")
    else:
        await message.answer("Мы уже играем.\n"
                             "Для отмены команды /cancel\n"
                             "Чтобы продолжить играть присылайте число от 1 до 100")
                        

# хендлер срабатываюзий при отправке пользователем число по условию и обрабатывающий число в игре
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def procces_answer_digit(message: Message):
    if user["in_game"]:
        answer_dig = int(message.text)  # число, которое пользровател отправил

        if answer_dig == user["dig"]:  # если число равно загаданному
            user["in_game"] = False
            user["dig"] = None
            user["attemp"] = None
            user["win"] += 1
            user["tot_game"] += 1
            await message.answer("Поздравляю! Вы угадали число!\n"
                                 "Сыграем еще раз?")
        else:  # если число неугадано
            if user["attemp"] > 0:  # если попытки еще остались
                if answer_dig > user["dig"]:  # если загаданное число меньше предложеного
                    user["attemp"] -= 1
                    await message.answer("Вы не угадали число.\n"
                                         "Загаданное число меньше предложенного вами.")
                else:  # если загаданное число меньше предложенного
                    user["attemp"] -= 1
                    await message.answer("Вы не угадали число.\n"
                                         "Загаданное число больше вашего.")
            else:  # если число не угадано и попыток больше не осталось
                user["in_game"] = False
                user["dig"] = None
                user["attemp"] = None
                user["tot_game"] += 1
                await message.answer("Вы не угадали число.\n"
                                     "К сожалению попытки закончились. Вы проиграли.\n"
                                     "Начать игру занова?")
    else:
        await message.answer("Мы еще не играем.\n"
                             "Хоите сыграть?")


# хэндлер будет срабатывать на любые остальные сообщения
@dp.message()
async def procces_other_message(message: Message):
    if user["in_game"]:
        await message.answer("Мы же сейчас играем.\n"
                             "Присылайте числа от 1 до 100")
    else:
        await message.answer("Пока что я довольно ограниченный бот.\n"
                             "Поэтому давайте просто поиграем =)")



if __name__ == "__main__":
    dp.run_polling(BOT)
        




                    

                

