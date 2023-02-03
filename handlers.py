import random

from aiogram import types
from loader import dp

max_count = 150
total = 0
new_game = False
duel = []
first = 0
current = 0


@dp.message_handler(commands=['start', 'старт'])
async def mes_start(message: types.Message):
    name = message.from_user.first_name
    await message.answer(f'{name}, привет! Сегодня сыграем с тобой в конфеты! \n'
                         f'Для начала игры c ботом введи команду /game_bot.\n '
                         f'Или /duel для игры c противником\n'
                         f'Для настройки конфет введи команду /set и укажи количество конфет\n'
                         f'/exit - для досрочного прекращения игры')
    print(message.from_user.id)


@dp.message_handler(commands=['game_bot'])
async def mes_new_game(message: types.Message):
    global new_game
    global total
    global max_count
    global first
    global duel
    if duel == []:
        duel.append(int(message.from_user.id))
        new_game = True
        total = max_count
        first = random.randint(0, 1)
        if first:
            await message.answer(f'Игра началась. По жребию первым ходит {message.from_user.first_name}! \n'
                                 f'Бери конфеты...')
        else:
            await message.answer(f'Игра началась. По жребию первым ходит Ботяо')
            await bot_turn(message)
    else:
        await message.answer(f'Бот пока занят, загляните попозже>')


@dp.message_handler(commands=['duel'])
async def mes_duel(message: types.Message):
    global new_game
    global total
    global max_count
    global duel
    global first
    global current
    if new_game:
        await message.answer(f'Игра уже идет! Нельзя начать новую игру.\n'
                             f'/exit - для выхода из игры!')
    else:
        if int(message.from_user.id) in duel:
            await message.answer(f'Противник пока не появился\n'
                                 f'/exit - для выхода из игры!')
        else:
            duel.append(int(message.from_user.id))
        if len(duel) < 2:
            await message.answer(f'Ожидай противника!')
        else:
            new_game = True
            total = max_count
            await dp.bot.send_message(duel[0], f'Противник найден! Игра началась! Cтартовое кол-во конфет {total}')
            await dp.bot.send_message(duel[1], f'Противник найден! Игра началась! Cтартовое кол-во конфет {total}')
            first = random.randint(0, 1)
            if first:
                await dp.bot.send_message(duel[0], 'Первый ход за тобой, бери конфеты')
                await dp.bot.send_message(duel[1], 'Первый ход за твоим противником! Жди своего хода')
            else:
                await dp.bot.send_message(duel[1], 'Первый ход за тобой, бери конфеты')
                await dp.bot.send_message(duel[0], 'Первый ход за твоим противником! Жди своего хода')
            current = duel[0] if first else duel[1]
            new_game = True


@dp.message_handler(commands=['exit'])
async def mes_exit(message: types.Message):
    global current
    global duel
    global new_game
    if len(duel) > 0:
        if int(message.from_user.id) in duel:
            if len(duel) == 1:
                await message.answer(f'Игра прервана. \n/start - для вызова меню')
            else:
                i, j = 0, 1
                if duel[1] == int(message.from_user.id):
                    i, j = j, i
                await dp.bot.send_message(duel[i], 'Игра прервана! \n/start - для вызова меню')
                await dp.bot.send_message(duel[j], 'Твой противник покинул игру!\n/start - для вызова меню')
            new_game = False
            duel = []
        else:
            await message.answer(f'Идет игра! Ожидайте свободного слота!')
    else:
        await message.answer(f'Игра не была начата! '
                             f'Для начала игры c ботом введи команду /game_bot.\n'
                             f'Или /duel для игры c противником')


@dp.message_handler(commands=['set'])
async def mes_set(message: types.Message):
    global max_count
    global new_game
    name = message.from_user.first_name
    if len(message.text)>5:
        count = message.text.split()[1]
        if not new_game:
            if count.isdigit() and int(count)> 0:
                max_count = int(count)
                await message.answer(f'Конфет теперь будет {max_count} ')
            else:
                await message.answer(f'{name}, напишите число больше нуля.')
        else:
            await message.answer(f'{name}, нельзя менять правила во время игры')
    else:
        await message.answer(f'{name}, введи команду в формате: \n/set ЧИСЛО.\n Пример: /set 200')


@dp.message_handler()
async def mes_take_candy(message: types.Message):
    global new_game
    global total
    global max_count
    global duel
    global first
    name = message.from_user.first_name
    count = message.text
    if len(duel) == 1:
        if message.from_user.id in duel:
            if message.text.isdigit() and 0 < int(message.text) < 29:
                if int(count) <= total:
                    total -= int(message.text)
                    if total <= 0:
                        await message.answer(f'Ура! {name} ты победил!')
                        new_game = False
                        duel = []
                    else:
                        await message.answer(f'{name} взял {count} конфет. '
                                             f'На столе осталось {total}')
                        await bot_turn(message)
                else:
                    await message.answer(f'Можно взять не больше {total} конфет')
            else:
                await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28!')
        else:
            await message.answer(f'Бот занят, загляните попозже>')
    elif len(duel) == 2:
        if current == int(message.from_user.id):
            name = message.from_user.first_name
            count = message.text
            # if new_game:
            if message.text.isdigit() and 0 < int(message.text) < 29:
                if int(count) <= total:
                    total -= int(count)
                    if total <= 0:
                        await message.answer(f'Ура! {name} ты победил!')
                        await dp.bot.send_message(enemy_id(),
                                                  'К сожалению, ты проиграл! Твой оппонент оказался умнее! :)')
                        new_game = False
                        duel = []
                    else:
                        await message.answer(f'На столе осталось {total} конфет.\nОжидайте ход противника')
                        await dp.bot.send_message(enemy_id(),
                                                  f'Противник взял {count} конфет\n'
                                                  f'На столе осталось {total} '
                                                  f'Теперь твой ход! ')
                        switch_players()
                else:
                    await message.answer(f'Можно взять не больше {total} конфет')
            else:
                await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28!')
        else:
            await message.answer(f'Cейчас не твой ход!')
    else:
        await message.answer(f'Некорректный запрос!\n Нажмите /start для запуска.')


async def bot_turn(message: types.Message):
    global total
    global new_game
    global duel
    bot_take = 0
    if 0 < total < 29:
        bot_take = total
        total -= bot_take
        await message.answer(f'Бот взял {bot_take} конфет. '
                             f'На столе осталось {total} и бот одержал победу')
        new_game = False
        duel = []
    else:
        remainder = total % 29
        bot_take = remainder if remainder != 0 else 28
        total -= bot_take
        await message.answer(f'Бот взял {bot_take} конфет. '
                             f'На столе осталось {total}\n Твой ход! ')


def switch_players():
    global duel
    global current
    if current == duel[0]:
        current = duel[1]
    else:
        current = duel[0]


def enemy_id():
    global duel
    global current
    if current == duel[0]:
        return duel[1]
    else:
        return duel[0]
