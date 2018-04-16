import flask
from telebot import types, TeleBot
from db.location import get_cities, get_regions
from db.company import get_companies, get_company_info
from db.comment import save_comment, get_comments
from models.user import User, get_user, get_user_wrap, get_name_by_id
from config import TOKEN,WEBHOOK_HOST, WEBHOOK_PORT,\
    WEBHOOK_LISTEN, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH


bot = TeleBot(TOKEN)

app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'INDEX'


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(msg):
    user = get_user(msg)
    if not user:
        user = User(user_id=msg.from_user.id, name=msg.from_user.first_name, msg=msg)
        user.save()
        bot.send_message(user.id, '{}{}'.format('Здравствуйте, я помогу найти такси вашего города. ',
                                                'Для получения списка компаний укажите область и город'))
        show_regions(user)
    else:
        bot.send_message(user.id, f'Здравствуйте,{user.name}')
        home(user)


@bot.message_handler(func=lambda mess: 'Главное меню' == mess.text, content_types=['text'])
@get_user_wrap
def home(user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for text in ('Изменить местоположение', 'Выбрать компанию'):
        markup.add(types.KeyboardButton(text))

    loc = f'{user.region}, {user.city}'
    if user.region == user.city:
        loc = f'{user.city}'
    bot.send_message(user.id, f'Ваше местоположение {loc}', reply_markup=markup)


@bot.message_handler(func=lambda mess: 'Изменить местоположение' == mess.text, content_types=['text'])
@get_user_wrap
def show_regions(user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for region in get_regions(user):
        markup.add(types.KeyboardButton(region[0]))
    markup.add(types.KeyboardButton('Главное меню'))

    message = bot.send_message(user.id, 'Выбери область из списка ниже', reply_markup=markup)
    bot.register_next_step_handler(message, set_region)


@get_user_wrap
def set_region(user):
    if (user.msg.text,) in get_regions(user):
        user.region = user.msg.text
        user.update_location_by_region()
        show_cities(user)
    elif user.msg.text == 'Главное меню':
        home(user)
    else:
        bot.send_message(user.id, 'Простите, я не понимаю')
        home(user)


@get_user_wrap
def show_cities(user):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for city in get_cities(user):
        markup.add(types.KeyboardButton(city[0]))
    markup.add(types.KeyboardButton('Главное меню'))

    message = bot.send_message(user.id, 'Выберите  город', reply_markup=markup)
    bot.register_next_step_handler(message, set_city)


@get_user_wrap
def set_city(user):
    if (user.msg.text,) in get_cities(user):
        user.city = user.msg.text
        user.update_location()
        home(user)
    elif user.msg.text == 'Главное меню':
        home(user)
    else:
        bot.send_message(user.id, 'Простите, я не понимаю')
        home(user)


@bot.message_handler(func=lambda mess: 'Выбрать компанию' == mess.text, content_types=['text'])
def show_companies(msg, msg_id=0, start=0, end=8):
    companies = get_companies(get_user(msg))
    text = 'Я нашел {} компаний. Вы можете выбрать одну из них или найти информациюю о конкретной комании'\
           .format(len(companies))

    markup = types.InlineKeyboardMarkup()
    for name in companies[start:end]:
        markup.add(types.InlineKeyboardButton(name[0], callback_data='show_taxi_desc '+name[0]))

    pagination = []
    if start >= 8:
        pagination.append(types.InlineKeyboardButton('<<', callback_data='<< {} {}'.format(start, end)))
    if end < len(companies):
        pagination.append(types.InlineKeyboardButton('>>', callback_data='>> {} {}'.format(start, end)))
    markup.add(*pagination)
    markup.add(types.InlineKeyboardButton('Найти по названию', callback_data='find'))

    if msg_id:
        bot.edit_message_text(chat_id=msg.from_user.id, message_id=msg_id,
                              text=text,
                              reply_markup=markup)
    else:
        bot.send_message(msg.from_user.id, text=text, reply_markup=markup)
        home(msg)


def show_company_info(user):
    desc = get_company_info(user)
    user.last_company_id = desc[0]
    user.update_last_company()

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton('Оставить отзыв'), types.KeyboardButton('Посмотреть отзывы'))
    markup.add(types.KeyboardButton('Главное меню'))

    bot.send_message(user.id, '{}\n\n{}'.format(desc[1], desc[2]), reply_markup=markup)


@bot.message_handler(func=lambda mess: 'Оставить отзыв' == mess.text, content_types=['text'])
@get_user_wrap
def request_comment(user):
    message = bot.send_message(user.id, 'Введите свой комментарий')
    bot.register_next_step_handler(message, send_comment)


@get_user_wrap
def send_comment(user):
    save_comment(user)
    show_comments(user)
    return 0


@bot.message_handler(func=lambda mess: 'Посмотреть отзывы' == mess.text, content_types=['text'])
@get_user_wrap
def to_comments(user):
    show_comments(user)


def show_comments(user, msg_id=0, c=0):
    comments = get_comments(user)
    if not comments:
        bot.send_message(user.id, 'Отзывов нет')
        home(user)
        return 0

    current = comments[c]
    comment = f'{get_name_by_id(current[0])}\n{current[1]}\n\n{current[2]}'

    markup = types.InlineKeyboardMarkup()
    pagination = []

    if c > 0:
        pagination.append(types.InlineKeyboardButton('<<', callback_data='<c {}'.format(c)))
    if c < len(comments)-1:
        pagination.append(types.InlineKeyboardButton('>>', callback_data='>c {}'.format(c)))

    markup.add(*pagination)
    if msg_id:
        bot.edit_message_text(chat_id=user.id, message_id=msg_id,
                              text=comment,
                              reply_markup=markup)
    else:
        bot.send_message(user.id, comment, reply_markup=markup)
        home(user)
    return 0


@bot.callback_query_handler(func=lambda call: '<c' in call.data or '>c' in call.data)
def comment_pagination_callback(call):
    data = call.data.split(' ')
    cur = int(data[-1])
    if '>c' in data:
        cur += 1
    elif '<c' in data:
        cur -= 1
    show_comments(get_user(call), call.message.message_id, cur)


@bot.callback_query_handler(func=lambda call: '<<' in call.data or '>>' in call.data)
def pagination_callback(call):
    data = call.data.split(' ')
    start, end = int(data[-2]), int(data[-1])
    if '>>' in data:
        start, end = start+8, end+8
    elif '<<' in data:
        start, end = start-8, end-8
    show_companies(call, call.message.message_id, start, end)


@bot.callback_query_handler(func=lambda call: 'show_taxi_desc' in call.data)
@get_user_wrap
def set_company_name(user):
    try:
        name = user.msg.data.split(' ')[-1]
    except AttributeError:
        name = user.msg.text

    if (name,) in get_companies(user):
        user.last_company = name
        show_company_info(user)
        return 0
    else:
        bot.send_message(user.id, 'Простите, возникла ошибка. Попробуйте позже')


@bot.callback_query_handler(func=lambda call: 'find' in call.data)
def request_company_name(call):
    message = bot.send_message(call.from_user.id, 'Введите название компании')
    bot.register_next_step_handler(message, set_company_name)


"""
# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
"""

if __name__ == '__main__':
    bot.polling()
