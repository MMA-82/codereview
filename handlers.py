import random

from aiogram import types
from loader import dp

max_count = 100
total = 0
new_game = False
duel = []
first = 0
current = 0
chapters = ['/rules - правила игры ',
            '/help - что делать ',
            '/new_game - новая игра ',
            '/duel + id оппонента - игра вдвоем']


@dp.message_handler(commands=['start', 'старт'])
async def mes_start(message: types.Message):
    global chapters
    name = message.from_user.first_name
    await message.answer(f'{name}, привет! Здесь можно сыграть в конфеты!')
    print(message.from_user.id)
    for item in chapters:
        await message.answer(f'\t{item}')

@dp.message_handler(commands=['rules'])
async def mes_rules(message: types.Message):
    await message.answer('На столе некоторое количество конфет. ' 
                        '\nОппоненты поочередно берут со стола конфеты. '
                        '\nЗа один ход можно взять не более 28 конфет. '
                        '\nКто возьмет последние конфеты со стола, тот и выиграл!')

@dp.message_handler(commands=['help'])
async def mes_help(message: types.Message):
    await message.answer('Введите /new_game чтобы начать игру. ' 
                        '\nНа столе по умолчанию 100 конфет. '
                        '\nЕсли хотите установить другое число, введите /set и после пробела напишите желаемое число конфет на столе. '
                        '\nЕсли хотите сыграть с другим ироком, введите /duel и id оппонента.')


@dp.message_handler(commands=['new_game'])
async def mes_new_game(message: types.Message):
    global new_game
    global total
    global max_count
    global first
    new_game = True
    total = max_count
    first = random.randint(0,1)
    if first:
        await message.answer(f'Игра началась. По жребию первым ходит {message.from_user.first_name}. '
                            f'\nНа столе {total} конфет, бери конфеты!')
    else:
        await message.answer(f'Игра началась. На столе {total} конфет. По жребию первым ходит Ботяо')
        await bot_turn(message)


@dp.message_handler(commands=['duel'])
async def mes_duel(message: types.Message):
    global new_game
    global total
    global max_count
    global duel
    global first
    global current
    duel.append(int(message.from_user.id))
    duel.append(int(message.text.split()[1]))
    total = max_count
    first = random.randint(0,1)
    if first:
        await dp.bot.send_message(duel[0], 'Первый ход за тобой, бери конфеты')
        await dp.bot.send_message(duel[1], 'Первый ход за твоим противником! Жди своего хода')
    else:
        await dp.bot.send_message(duel[1], 'Первый ход за тобой, бери конфеты')
        await dp.bot.send_message(duel[0], 'Первый ход за твоим противником! Жди своего хода')
    current = duel[0] if first else duel[1]
    new_game = True


@dp.message_handler(commands=['set'])
async def mes_set(message: types.Message):
    global max_count
    global new_game
    name = message.from_user.first_name
    count = message.text.split()[1]
    if not new_game:
        if count.isdigit():
            max_count = int(count)
            await message.answer(f'На столе теперь {max_count} конфет. '
                                '\nВведите /new_game чтобы начать игру.')
        else:
            await message.answer(f'{name}, напишите цифрами!')
    else:
        await message.answer(f'{name}, нельзя менять правила во время игры!')


@dp.message_handler()
async def mes_take_candy(message: types.Message):
    global new_game
    global total
    global max_count
    global duel
    global first
    name = message.from_user.first_name
    count = message.text
    if len(duel) == 0:
        if new_game:
            if count.isdigit() and 0 < int(count) < 29:
                total -= int(count)
                if total <= 0:
                    await message.answer(f'Ура! {name} ты победил! '
                                        '\nВведите /new_game чтобы сыграть еще раз.')
                    new_game = False
                else:
                    await message.answer(f'{name} взял {count} конфет. '
                                         f'На столе осталось {total}')
                    await bot_turn(message)
            else:
                await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28!')
    else:
        if current == int(message.from_user.id):
            name = message.from_user.first_name
            count = message.text
            if new_game:
                if count.isdigit() and 0 < int(count) < 29:
                    total -= int(count)
                    if total <= 0:
                        await message.answer(f'Ура! {name} ты победил! '
                                            '\nВведите /new_game чтобы сыграть еще раз.')
                        await dp.bot.send_message(enemy_id(), 'К сожалению ты проиграл! Твой оппонент оказался умнее! :)')
                        new_game = False
                    else:
                        await message.answer(f'{name} взял {count} конфет. '
                                             f'На столе осталось {total}')
                        await dp.bot.send_message(enemy_id(), f'Теперь твой ход, бери конфеты! На столе осталось ровно {total}')
                        switch_players()
                else:
                    await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28!')


async def bot_turn(message: types.Message):
    global total
    global new_game
    bot_take = 0
    if 0 < total < 29:
        bot_take = total
        total -= bot_take
        await message.answer(f'Бот забрал последние {bot_take} конфет, и одержал победу!'
                            '\nВведите /new_game чтобы сыграть еще раз.')
        new_game = False
    else:
        remainder = total%29
        bot_take = remainder if remainder != 0 else 28
        total -= bot_take
        await message.answer(f'Бот взял {bot_take} конфет. '
                            f'На столе осталось {total}, {message.from_user.first_name}, твой ход!')

def switch_players():
    global duel
    global current
    current == duel[1] if current == duel[0] else current == duel[0]
      
def enemy_id():
    global duel
    global current
    if current == duel[0]: 
        return duel[1]    
    else:
        return duel[0]