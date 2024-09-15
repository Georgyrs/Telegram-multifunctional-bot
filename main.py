import datetime
import os
import random
import sqlite3
import time
import requests
import telebot
import wikipedia
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
bot = telebot.TeleBot(config.BOT_TOKEN)
wikipedia.set_lang(config.WIKIPEDIA_LANGUAGE)


def get_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


current_date = get_time()


def get_weather():
    url = config.WEATHER_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    temperature_element = soup.find("span", {"class": "t_0"})
    temperature = temperature_element.text.strip() if temperature_element else "N/A"

    a = config.WEATHER_API_URL
    so = requests.get(a).text
    s = BeautifulSoup(so, 'html.parser')
    current_weather = None
    for r in s.find_all('div', class_="forecast-14-day"):
        current_weather = r.find('td', class_="precip-line").text.strip()

    return temperature, current_weather


# факты
news_list = ['Алексей из 8-В откровенный гомосексуал легкого поведения',
             'Жена - главный сталкер планеты, знает даже время когда вы какаете']
factweb = "https://xn--80af2bld5d.xn--p1ai/studlife/home/10565/"
getreq = requests.get(factweb).text
bs = BeautifulSoup(getreq, 'html.parser')
facts = bs.find('div', class_="white-box col-margin-bottom padding-box").text.strip()
facts_list = [fact.strip() for fact in facts.split('\n') if fact.strip()]

for fact in facts_list:
    if fact.startswith("Факт №"):
        fact_index = facts_list.index(fact)
        news_list.append(facts_list[fact_index + 1])

conn = sqlite3.connect(config.DATABASE_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS ships (
                    chat_id INTEGER,
                    user1 TEXT,
                    user2 TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                    chat_id INTEGER,
                    event_date TEXT,
                    event_name TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER,
                    user_id INTEGER,
                    balance INTEGER DEFAULT 0
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    job_name TEXT,
                    min_payment INTEGER,
                    max_payment INTEGER
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS upgrades (
                    upgrade_name TEXT,
                    cost INTEGER
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS user_upgrades (
                    user_id INTEGER,
                    chat_id INTEGER,
                    upgrade_name TEXT,
                    PRIMARY KEY (user_id, chat_id, upgrade_name)
                )''')
conn.commit()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS message_stats (
        user_id INTEGER,
        chat_id INTEGER,
        message_date TEXT,
        message_count INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, chat_id, message_date)
    )
''')
conn.commit()


def delete_all_ships():
    cursor.execute('DELETE FROM ships')
    conn.commit()


def delete_all_business():
    cursor.execute('DELETE FROM last_income_time')
    conn.commit()


@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for new_user in message.new_chat_members:
        bot.send_message(message.chat.id,
                         f"*Добро пожаловать в 8-В, {new_user.first_name}"
                         f"!🥳🥂*\nДля того, чтобы ознакомиться со мной пропиши руководство.",
                         parse_mode='Markdown')


def add_ship(chat_id, user1, user2):
    cursor.execute('INSERT INTO ships (chat_id, user1, user2) VALUES (?, ?, ?)', (chat_id, user1, user2))
    conn.commit()


def get_ships(chat_id):
    cursor.execute('SELECT user1, user2 FROM ships WHERE chat_id = ?', (chat_id,))
    return cursor.fetchall()


def add_event(chat_id, event_date, event_name):
    cursor.execute('INSERT INTO events (chat_id, event_date, event_name) VALUES (?, ?, ?)',
                   (chat_id, event_date, event_name))
    conn.commit()


def get_events(chat_id):
    cursor.execute('SELECT event_date, event_name FROM events WHERE chat_id = ?', (chat_id,))
    return cursor.fetchall()


def remove_expired_events(current_date):
    cursor.execute('DELETE FROM ships')
    cursor.execute('DELETE FROM events WHERE event_date < ?', (current_date,))
    conn.commit()


def check_and_notify_events():
    new_cursor = conn.cursor()
    new_cursor.execute('SELECT chat_id, event_name FROM events WHERE event_date = ?', (current_date,))
    events = new_cursor.fetchall()
    for chat_id, event_name in events:
        bot.send_message(chat_id, f"🚨 *ВНИМАНИЕ!* СЕГОДНЯ ВАЖНАЯ ДАТА: *{event_name}*", parse_mode='Markdown')
        new_cursor.execute('DELETE FROM events WHERE chat_id = ? AND event_name = ?', (chat_id, event_name))
    conn.commit()
    new_cursor.close()


def init_jobs():
    jobs = [
        ("Проститутка", 0, 0),
        ("Дворник", 50, 100),
        ("Продавец", 100, 150),
        ("Программист", 200, 300),
        ("Бизнесмен", 350, 999)
    ]

    cursor.executemany('INSERT INTO jobs (job_name, min_payment, max_payment) VALUES (?, ?, ?)', jobs)
    conn.commit()


init_jobs()


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.lower().strip()

    if text.startswith('start'):
        respond_start(message)
    elif text.startswith('руководство'):
        respond_help(message)
    elif text.startswith('шип'):
        respond_ship(message)
    elif text.startswith('список шипов'):
        respond_ships(message)
    elif text.startswith('пугалка'):
        pugalka(message)
    elif text.startswith('математика'):
        respond_biology(message)
    elif text.startswith('событие_создать'):
        dates(message)
    elif text.startswith('даты'):
        showdates(message)
    elif text.startswith('погода'):
        show_weather(message)
    elif text.startswith('списать'):
        wiki_search(message)
    elif text.startswith('рп'):
        rp_commands(message)
    elif text.startswith('факт'):
        randomfact(message)
    elif text.startswith('работать'):
        work(message)
    elif text.startswith('шоп'):
        openshop(message)
    elif text.startswith('кошелек') or text.startswith('кошелёк'):
        check_balance(message)
    elif text.startswith('ограбить'):
        steal_money(message)
    else:
        pass
    check_and_notify_events()


def respond_start(message):
    response = "*Здравствуйте!* Я бот созданный специально для 8-В! Напишите *руководство* чтобы узнать команды."
    bot.send_message(message.chat.id, response, parse_mode='Markdown')


def respond_help(message):
    response = "*Команды:*\n\n"
    response += "• *шип @1 @2* – для создания шипа.\n"
    response += "• *список шипов* – покажет все шипы.\n"
    response += "• *пугалка* – комната страха для Симы.\n"
    response += "• *математика* – получите случайную оценку по математике.\n"
    response += "• *событие_создать* – создать событие. Формат: *дата событие*\n"
    response += "• *даты* – покажет все важные события.\n"
    response += "• *погода* – текущая погода.\n"
    response += "• *списать <тема>* – отправит информацию о запросе.\n"
    response += "• *рп <действие> @<user>* – отправит действие которое вы совершили над юзером.\n"
    response += "• *факт* – отправит случайный факт о мире.\n"
    response += "• *работать* – выполните случайную работу и получите монеты. КД: 2 часа.\n"
    response += "• *шоп* – магазин предметов.\n"
    response += "• *кошелек* – Ваш баланс.\n"
    response += "• *ограбить @* – Украсть деньги у пользователя.\n"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')


def respond_ship(message):
    try:
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message, "*Неверный формат команды.* Используйте: *шип @1 @2*", parse_mode='Markdown')
            return

        user1_username = command_parts[1].replace('@', '').strip()
        user2_username = command_parts[2].replace('@', '').strip()

        if user1_username == user2_username:
            bot.reply_to(message, "*Нельзя создать шип с самим собой!*", parse_mode='Markdown')
            return
        user1_info = None
        user2_info = None
        for member in bot.get_chat_administrators(message.chat.id):
            if member.user.username == user1_username:
                user1_info = member.user
                user1_username = f"@{user1_username}"
            if member.user.username == user2_username:
                user2_info = member.user
                user2_username = f"@{user2_username}"

        if user1_info is None or user2_info is None:
            bot.reply_to(message,
                         "*Один или оба пользователя не находятся в этом чате или их невозможно найти по никнейму.*",
                         parse_mode='Markdown')
            return
        add_ship(message.chat.id, user1_username, user2_username)
        bot.reply_to(message, f"Шип между {user1_info.first_name} и {user2_info.first_name} создан!",
                     parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}", parse_mode='Markdown')


def respond_ships(message):
    ships = get_ships(message.chat.id)
    if not ships:
        bot.reply_to(message, "<b>Пока нет созданных шипов.</b>", parse_mode='html')
        return

    response = "<b>Список всех шипов:</b>\n"
    for user1, user2 in ships:
        response += f"• {user1} - {user2}\n"

    bot.send_message(message.chat.id, response, parse_mode='html')


def pugalka(message):
    a = random.randint(1, 6)
    media_paths = config.MEDIA_PATHS

    if a in media_paths:
        media_path = media_paths[a]
        if os.path.exists(media_path):
            with open(media_path, 'rb') as media:
                if media_path.endswith(('.jpg', '.jpeg', '.png')):
                    bot.send_photo(message.chat.id, media)

                elif media_path.endswith('.MP4'):
                    bot.send_video(message.chat.id, media)
                else:
                    bot.reply_to(message, "*Неподдерживаемый формат файла.*", parse_mode='Markdown')
        else:
            bot.reply_to(message, "*Файл не найден.*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "*Лохам пугалки не отправляю!*", parse_mode='Markdown')


def respond_biology(message):
    ocenka = random.randint(2, 5)
    if ocenka == 5:
        otvet = "*Продолжайте учиться в том же духе!* ✅"
    elif ocenka == 4:
        otvet = "*Нужно чуть-чуть подтянуть учебу!* 🤏🏻"
    elif ocenka == 3:
        otvet = "*Будьте осторожны! Елена Николаевна рассердится!* 😱"
    elif ocenka == 2:
        otvet = "*Ты Миша? Без комментариев...* 🙁"
    bot.send_message(message.chat.id, f"*Ваша следующая оценка по математике:* {ocenka}\n\n{otvet}",
                     parse_mode='Markdown')


def dates(message):
    try:
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message, "*Неверный формат команды.* Используйте: *дата событие*", parse_mode='Markdown')
            return

        date = command_parts[1].strip()
        event = command_parts[2].strip()

        add_event(message.chat.id, date, event)
        bot.reply_to(message, f"*Событие {event} создано!*\n\n*Дата:* {date}", parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"*Произошла ошибка:* {e}", parse_mode='Markdown')


def showdates(message):
    remove_expired_events(current_date)
    events = get_events(message.chat.id)
    if not events:
        bot.reply_to(message, "*Пока нет важных событий.*", parse_mode='Markdown')
        return

    response = "*Список всех событий:*\n"
    for date, event in events:
        response += f"• {date} - {event}\n"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')


def show_weather(message):
    temperature, current_weather = get_weather()
    advice = ""
    if current_weather == 'Кратковременный дождь':
        advice = "💦 Возможно, вам понадобятся зонтик и дождевик!"
    elif current_weather == 'Ясно':
        advice = "☀️ Отличный день для прогулки на улице!"
    elif current_weather == 'Малооблачно':
        advice = "⛅ Небо немного облачное, но в целом приятно!"
    elif current_weather == 'Облачно':
        advice = "☁️ Сегодня облачно, но дождя не ожидается."

    bot.send_message(message.chat.id, f"*Погода сейчас:* {temperature}, *{current_weather}* {advice}",
                     parse_mode='Markdown')


def wiki_search(message):
    if not message.text.lower().startswith('списать'):
        bot.reply_to(message, "*Используйте команду списать <запрос>*", parse_mode='Markdown')
        return
    command_parts = message.text.split(' ', 1)
    if len(command_parts) < 2:
        bot.reply_to(message, "*Пожалуйста, укажите запрос для поиска.*", parse_mode='Markdown')
        return

    word = command_parts[1].strip().lower()

    try:
        finalmess = wikipedia.summary(word)
        max_length = 4096
        if len(finalmess) > max_length:
            part1 = finalmess[:max_length].strip()
            part2 = finalmess[max_length:].strip()
            bot.send_message(message.chat.id, part1, parse_mode='html')
            bot.send_message(message.chat.id, part2, parse_mode='html')
        else:
            bot.send_message(message.chat.id, finalmess, parse_mode='html')

    except wikipedia.exceptions.PageError:
        bot.send_message(message.chat.id, "Такой страницы не существует!")
    except Exception as e:
        bot.send_message(message.chat.id, f"*Произошла ошибка:* {e}", parse_mode='Markdown')


def rp_commands(message):
    random_phrase = ['Аааах, как приятно, наверное🥵', 'Как так можно вообще?!🤬', 'Ооой, да ты пошлый🔞',
                     'Кракен щас забанит тебя за такое!🔨']
    random_choice = random.choice(random_phrase)
    command_parts = message.text.split(' ', 2)
    if len(command_parts) < 3:
        bot.send_message(message.chat.id, "Invalid command format. Use: /command <action> @username")
        return

    action = command_parts[1].strip().lower()
    user = command_parts[2].strip()
    usercall = message.from_user
    usercalled = usercall.username

    if len(action) >= 2:
        last_two = action[-2:]
        action_modified = action[:-2] + 'л'
        response1 = f"@{usercalled} {action_modified} {user}! \n\n{random_choice}"
        bot.send_message(message.chat.id, response1)


def randomfact(message):
    random_fact = random.choice(news_list)
    bot.send_message(message.chat.id, f"*{random_fact}*", parse_mode='Markdown')


def get_balance(user_id, chat_id):
    cursor.execute('SELECT balance FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    result = cursor.fetchone()
    return result[0] if result else 0


def update_balance(user_id, chat_id, amount):
    cursor.execute('SELECT balance FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    result = cursor.fetchone()
    if result:
        new_balance = result[0] + amount
        cursor.execute('UPDATE users SET balance = ? WHERE user_id = ? AND chat_id = ?',
                       (new_balance, user_id, chat_id))
    else:
        cursor.execute('INSERT INTO users (chat_id, user_id, balance) VALUES (?, ?, ?)', (chat_id, user_id, amount))
    conn.commit()


def do_job(user_id, chat_id):
    cursor.execute('SELECT job_name, min_payment, max_payment FROM jobs ORDER BY RANDOM() LIMIT 1')
    job = cursor.fetchone()
    payment = random.randint(job[1], job[2])

    cursor.execute(
        'SELECT * FROM user_upgrades WHERE user_id = ? AND chat_id = ? AND upgrade_name = "Ускоритель заработка"',
        (user_id, chat_id))
    if cursor.fetchone():
        payment = int(payment * 1.5)

    update_balance(user_id, chat_id, payment)
    update_balance(1548224823, chat_id, -payment)
    cursor.execute('SELECT user_id FROM user_upgrades WHERE chat_id = ? AND upgrade_name = "Бизнес"', (chat_id,))
    business_owners = cursor.fetchall()

    if business_owners:
        business_profit = int(payment * 0.1)
        for owner in business_owners:
            business_owner_id = owner[0]
            if business_owner_id != user_id:
                update_balance(business_owner_id, chat_id, business_profit)
                bot.send_message(business_owner_id,
                                 f'💼 Вы получили {business_profit} монет за работу другого пользователя.')
    if job[0].lower() == "Проститутка":
        special_message = "💔 К сожалению, заказчику не понравился стриптиз, и он выдворил вас на улицу без оплаты. 🚪😔"
        bot.send_message(chat_id, special_message)
    return job[0], payment


cooldowns = {}
cooldowns_steal = {}


def can_work(user_id, chat_id):
    key = (user_id, chat_id)
    last_work_time = cooldowns.get(key)
    current_time = time.time()

    if last_work_time and (current_time - last_work_time) < 7200:
        return False, 7200 - (current_time - last_work_time)

    cooldowns[key] = current_time
    return True, 0


def work(message):
    init_jobs()

    user_id = message.from_user.id
    chat_id = message.chat.id
    can_work_now, time_left = can_work(user_id, chat_id)
    if not can_work_now:
        bot.reply_to(message, f"Вы уже работали недавно! Подождите еще {int(time_left // 60)} минут.")
        return

    job_name, payment = do_job(user_id, chat_id)
    balance = get_balance(user_id, chat_id)

    response = f"Вы выполнили работу '{job_name}' и заработали {int(payment)} монет! 💰\nВаш текущий баланс:" \
               f" {int(balance)} монет."
    update_balance(user_id, chat_id, payment)
    update_balance(1548224823, chat_id, -payment)
    bot.send_message(chat_id, response)

    if balance >= 2500:
        tax = int(balance * 0.02)
        update_balance(user_id, chat_id, -tax)
        update_balance(1548224823, chat_id, tax)
        update_balance(user_id, chat_id, payment)
        update_balance(1548224823, chat_id, -payment)
        balance = get_balance(user_id, chat_id)
        bot.send_message(chat_id, f'Налог 2% уплачен! 💸\nВаш новый баланс: {balance} 💰')


def check_balance(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    balance = get_balance(user_id, chat_id)
    response = f"Ваш текущий баланс 👛: {balance} монет."
    bot.send_message(chat_id, response)


def init_upgrades():
    upgrades = [
        ("Ускоритель заработка", 500),
        ("Улучшенный инструмент", 1000),
        ("Бизнес", 2000)
    ]

    cursor.executemany('INSERT INTO upgrades (upgrade_name, cost) VALUES (?, ?)', upgrades)
    conn.commit()


init_upgrades()


def buy_upgrade(user_id, chat_id, upgrade_name):
    cursor.execute('SELECT cost FROM upgrades WHERE upgrade_name = ?', (upgrade_name,))
    cost = cursor.fetchone()

    if cost:
        balance = get_balance(user_id, chat_id)
        if balance >= cost[0]:
            cursor.execute('SELECT * FROM user_upgrades WHERE user_id = ? AND chat_id = ? AND upgrade_name = ?',
                           (user_id, chat_id, upgrade_name))
            if cursor.fetchone():
                return "Вы уже купили это улучшение."

            update_balance(user_id, chat_id, -cost[0])
            update_balance(1548224823, chat_id, cost[0])
            cursor.execute('INSERT INTO user_upgrades (user_id, chat_id, upgrade_name) VALUES (?, ?, ?)',
                           (user_id, chat_id, upgrade_name))
            conn.commit()

            response = f"Вы успешно купили улучшение '{upgrade_name}' за {cost[0]} монет!" \
                       f" Ваш текущий баланс: {balance - cost[0]} монет."
        else:
            response = "Недостаточно средств для покупки этого улучшения."
    else:
        response = "Улучшение не найдено."

    return response


def openshop(message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1)
    item1 = InlineKeyboardButton("Ускоритель заработка - 500 монет", callback_data=f"buy_upgrade_accelerator_{user_id}")
    item2 = InlineKeyboardButton("Улучшенный инструмент - 1000 монет", callback_data=f"buy_upgrade_tool_{user_id}")
    item3 = InlineKeyboardButton("Бизнес - 2000 монет", callback_data=f"buy_upgrade_business_{user_id}")

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, "Добро пожаловать в магазин! Выберите улучшение:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def callback_buy_item(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data, original_user_id = call.data.rsplit("_", 1)
    original_user_id = int(original_user_id)
    if user_id != original_user_id:
        return
    if data == "buy_upgrade_accelerator":
        response = buy_upgrade(user_id, chat_id, "Ускоритель заработка")
    elif data == "buy_upgrade_tool":
        response = buy_upgrade(user_id, chat_id, "Улучшенный инструмент")
    elif data == "buy_upgrade_business":
        response = buy_upgrade(user_id, chat_id, "Бизнес")
    else:
        response = "Неизвестный товар."

    bot.send_message(chat_id, response)


def can_steal(user_id, chat_id):
    key = (user_id, chat_id)
    last_steal_time = cooldowns_steal.get(key)
    current_time = time.time()

    if last_steal_time and (current_time - last_steal_time) < 3600:
        return False, 3600 - (current_time - last_steal_time)

    cooldowns_steal[key] = current_time
    return True, 0


def steal_money(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    can_steal_now, time_lefts = can_steal(user_id, chat_id)
    if not can_steal_now:
        bot.reply_to(message, f"Вы уже воровали! Подождите еще {int(time_lefts // 60)} минут.")
        return

    luck = random.randint(1, 2)
    command_parts = message.text.split(' ', 1)
    if len(command_parts) < 2:
        bot.reply_to(message, "*Неверный формат команды.* Используйте: *ограбить @Evgeni*", parse_mode='Markdown')
        return

    target_username = command_parts[1].replace('@', '').strip()
    target_user = None

    try:
        for member in bot.get_chat_administrators(chat_id):
            if member.user.username == target_username:
                target_user = member.user
                break

        if target_user is None:
            bot.reply_to(message, "*Пользователь не найден в этом чате.*", parse_mode='Markdown')
            return

        target_id = target_user.id
        if user_id == target_id:
            bot.reply_to(message, "*Нельзя своровать у самого себя!*", parse_mode='Markdown')
            return

        target_balance = get_balance(target_id, chat_id)
        if target_balance < 500:
            bot.reply_to(message, "*Только вы хотели обокрасть человека, как увидели его положение.\n"
                                  "Ваше сердце растопилось и вы дали ему 400 монет*", parse_mode='Markdown')
            update_balance(user_id, chat_id, -400)
            update_balance(target_id, chat_id, 400)
            return

        if luck == 1:
            stolen_amount = random.randint(50, 400)

            if stolen_amount > target_balance:
                stolen_amount = target_balance

            update_balance(target_id, chat_id, -stolen_amount)
            update_balance(user_id, chat_id, stolen_amount)

            thief_balance = get_balance(user_id, chat_id)
            new_target_balance = get_balance(target_id, chat_id)

            bot.send_message(chat_id, f"💸 *{message.from_user.first_name}* украл у *{target_user.first_name}* "
                                      f"{int(stolen_amount)} монет! Теперь у *{message.from_user.first_name}* "
                                      f"{int(thief_balance)} монет, а у *{target_user.first_name}* "
                                      f"{int(new_target_balance)} монет.", parse_mode='Markdown')
        else:
            update_balance(user_id, chat_id, -500)
            bot.send_message(chat_id,
                             "Только вы сунули руку в карман,"
                             " как офицер полиции обратил на вас внимание. Унося ноги вы выронили 500 монет")
    except Exception as e:
        bot.reply_to(message, f"*Произошла ошибка:* {e}", parse_mode='Markdown')


bot.polling(none_stop=True)
