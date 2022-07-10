import logging
import os
import pandas as pd
import pytz
import re
import numpy as np
import time

from telegram import *
from telegram.ext import *
from requests import *

import yoomoney
from yoomoney import Quickpay
from yoomoney import Client

import datetime
from datetime import datetime
from datetime import timedelta

import threading
from threading import Timer


# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

session_list_dic = {
    'psycodynamic':
        {'name':"Психодинамическая группа",
         'date_time':"по четвергам, 20:00 МСК",
         'reminder':"3_20:00",
         'specialist':"Фёдор Коньков",
         'picture':"NULL",
         'description':"Продолжительность - 10 недель",
         'invite': f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"2",
         'limit':15,
         'members':{},
         'queue':{}},
    'volunteertraining':
        {'name':"Группа поддержки для тех, кто помогает другим профессионально или как волонтёр",
         'date_time':"раз в неделю, 10 недель",
         'reminder':"",
         'specialist':"Фёдор Коньков",
         'picture':"NULL",
         'description':"* Выгорание - как избежать и что делать если оно вас настигло\n"
                       "* Сапожник без сапог - как научиться заботиться о себе, даже если вы хорошо умеете заботиться о других\n"
                       "* Проекция - как избежать видеть себя в клиенте\n"
                       "* Эмпатия - когда она помогает, а когда мешает\n"
                       "* Границы - как то что мы не делаем и не позволяем себе и другим может помогать вам и другим добиться хороших долговременных результатов\n"
                       "* Также психологи ответят на различные ваши вопросы о том как помогать эффективно и безопасно для всех\n\n"
                       "* Фокус - как позитивно и эффективно пережить перемены в ситуации неопределенности, открыть новые горизонты в себе, окружающих, и мире.\n\n"
                       "* Активный бмен личным опытом, чувствами, переживаниями. Возможность получить поддержку, обратную связь, новые навыки, в доброжелательный обстановке.\n\n"
                       "* Психолог поможет создать безопасную, свободную и творчесткую атмосферу для достижения группой и каждым участником максимального позитивных результатов. Полученный опыт, навыки и знания помогут с существующими и предстоящими жизненными ситуациями.",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':20,
         'members':{},
         'queue':{}},
    'meditation':
        {'name':"Медитация",
         'date_time':"по понедельникам, 21:30 МСК",
         'reminder':"0_21:30",
         'specialist':"Надежда Серебряникова",
         'picture':"NULL",
         'description':"Продолжительность - 10 недель",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':20,
         'members':{},
         'queue':{}},
    'metoday':
        {'name':"Группа для подростков 13-15 лет \"Я сегодня\"",
         'date_time':"по понедельникам, 19:00 МСК",
         'reminder':"0_19:00",
         'specialist':"Надежда Серебряникова",
         'picture':"NULL",
         'description':"Это группа для детей, которые  после переезда:\n"
                       "* ощущают себя дезориентированным, потерянным;\n"
                       "* проявляют апатию, отсутствие интереса к чему-либо;\n"
                       "* замыкаются в себе, отказываются говорить о своих чувствах;\n"
                       "* испытывают высокую тревогу, плохо спят;\n"
                       "* отказываются принимать новое место жизни, требуют вернуть их домой;\n"
                       "* проявляют агрессию, устраивают протесты\n\n"
                       "Продолжительность - 8 встреч по 1.5 часа",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':10,
         'members':{},
         'queue':{}},
    'protest':
        {'name':"Группа \"Протест\"",
         'date_time':"по вторникам, 19:00 МСК",
         'reminder':"1_19:00",
         'specialist':"Александра Иванова",
         'picture':"NULL",
         'description':"История протестного движения в России последние лет 10 - это история людей, которые сказали \"я - против\" и оказались предателями своей своей страны. А о предателях не принято говорить.\n"
                       "Так нам предлагают думать властьимущие."
                       "И когда теми, кто принимает устрашающие людей законы, движет страх, людьми, выходящих на митинги, не боящихся сказать свое мнение, движет сила, совесть и невозможность молчать. "
                       "Так случилось, что эти качества не в почете. А говорить то, что думаешь, с каждым днём всё опаснее.\n\n"
                       "Человек, который столкнулся с непростым опытом, с насилием, может сломаться. Обычная жизнь \"после\" начинает подчиняться внутренним страхам в следствие пережитого опыта.\n\n"
                        "Возможно, Вы именно тот человек, который столкнулся с таким опытом. И наша группа будет для Вас тем безопасным пространством, где можно говорить обо всем. И, самое главное, о своей боли и страхах.\n\n"
                       "Для кого эта группа:\n"
                       "* Вы не понимаете, что с Вами происходит\n"
                       "* Вы боитесь обращаться за поддержкой и помощью\n"
                       "* Вы задаетесь вопросом \"что будет дальше?\" и не знаете ответ\n"
                       "* Вам знакома бессонница, потеря аппетита, кошмары\n"
                       "* человек в форме вызывает ужас и панику\n"
                       "* Вы чувствуете, что перестали справляться с простыми привычными  делами\n"
                       "* Вы не чувствуете себя в безопасности\n\n"
                       "Продолжительность -  8 встреч по 1,5 часа.",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':15,
         'members':{},
         'queue':{}},
    'movingout':
        {'name':"Группа для переезжающих/переехавших",
         'date_time':"по пятницам, 19:00 МСК",
         'reminder':"4_19:00",
         'specialist':"Александра Иванова",
         'picture':"NULL",
         'description':"Эмиграция относится к сильнейшим стоессам. Человеку приходится одновременно принимать потерю прежнего образа жизни  и усваивать нормы и правила новой стране.  И нередко вопросы \"кто я?\", \"Где мое место в мире?\", становятся актуальными, как никогда. Психическая нагрузка довольна сильная, эмоции становятся трудно выносимыми.\n\n"
                       "Мы открываем набор в группу для тех, кому трудно в этих непростых условиях. Эта группа для вас, если:\n\n"
                       "* вы планируете переезд\n"
                       "* вас не понимают близкие и/или вы испытываете чувство вины перед теми, кто остаётся\n"
                       "* вы переехали и вам трудно даются этапы адаптации\n"
                       "* вы не испытываете того ожидаемого чувства \"ну наконец-то!\"\n"
                       "* все текущие бытовые дела даются вам с трудом в новой стране\n"
                       "* вам трудно найти свой круг общения\n"
                       "* вы переехали и экстренно и до сих пор не понимаете, что происходит\n"
                       "* вы часто задаетесь вопросом \"правильно ли я поступил_а?\"\n"
                       "* вам сложно на новом месте по непонятным причинам\n"
                       "* свой вариант\n\n"
                       "Продолжительность - 8 встреч по 1,5 часа.",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':15,
         'members':{},
         'queue':{}},
    'stayinrussia':
        {'name':"Я остаюсь!",
         'date_time':"по вторникам, 19:00 МСК",
         'reminder':"1_19:00",
         'specialist':"Татьяна",
         'picture':"NULL",
         'description':"Группа для тех, кто принял для себя непростое решение остаться в России.\n\n"
                       "Те из нас, кто остался в России в эти непростые времена, сталкивается с определёнными трудностями. Здесь мы также встречаемся со страхом, неопределённостью, ощущением одиночества и разделённости. Поэтому сейчас каждому из нас как никогда нужна поддержка и чувство \"Я не один\".\n\n"
                       "Продолжительность - 5 недель.",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':10,
         'members':{},
         'queue':{}},
    'arttheraty':
        {'name':"Арт-терапия",
         'date_time':"по пятницам, 18:00 МСК",
         'reminder':"4_18:00",
         'specialist':"Надежда Балицкая",
         'picture':"NULL",
         'description':"Продолжительность - 8 недель.",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':10,
         'members':{},
         'queue':{}},
    'forparents':
        {'name':"Группа для родителей",
         'date_time':"по средам, 19:00 МСК",
         'reminder':"2_19:00",
         'specialist':"Дина Палеха",
         'picture':"NULL",
         'description':"\"Как сохранить себя, психику и отношения с детьми в условиях тотальной нестабильности\""
                       "Каждый день нам всем приходится принимать какие-то решения. Но если ты родитель, то эти решения - не только за себя.\n\n"
                       "* Как справиться с этим грузом ответственности и не провалиться в собственные детские страхи?\n"
                       "* Как разрешить себе - взрослому- проживание сложных чувств?]n"
                       "* Как научить ребёнка проживать свои?\n"
                       "* Как успокоить ребёнка, не впадая в собственную тревогу?\n"
                       "* Может ли родитель быть слабым?\n"
                       "* Как выстраивать диалог с близкими, не впадая в агрессию и не ранясь?\n"
                       "* Как говорить с детьми о важном и сложном?\n\n"
                       "Эти и другие вопросы мы разберём в закрытой группе для родителей. Группе для тех, кто каждый день принимает решения не только за себя. И сам при этом нуждается в эмоциональной поддержке.\n\n"
                       "Продолжительность - 5 недель",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':10,
         'members':{},
         'queue':{}},
    'blackbox':
        {'name':"Черный ящик",
         'date_time':"по пятницам, 20:30 МСК",
         'reminder':"4_20:30",
         'specialist':"",
         'picture':"NULL",
         'description':"Я есть и я здесь.\n\n"
                       "Продолжительность - 5 недель",
         'invite':f"Meeting ID: 230 365 3201 | Passcode: gaXp8U | <a href='https://us05web.zoom.us/j/2303653201?pwd=WWJ1a3ZoblVFWTJIRHh4cGt6K0ppdz09'>Zoom</a>",
         'opengroup':"0",
         'limit':15,
         'members':{},
         'queue':{}},
    'crisis':
        {'name':"Краткосрочная терапия",
         'date_time':"в удобное для Вас время по договоренности с терапевтом",
         'reminder':"",
         'specialist':"Терапевт-волонтер сообщества @helpwithoutprejudice",
         'picture':"NULL",
         'description':"Личная краткосрочная терапия для тех, кому срочно необходима поддержка",
         'invite':f"",
         'opengroup':"0",
         'limit':0,
         'members':{},
         'queue':{}}
}

admin_cids = ['5358195597']

# We define command handlers. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Sends a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Sends a message when the command /help is issued."""
    help_message = f"Вот список команд, которые понимает наш бот:\n /start - начать работу с ботом\n /help - посмотреть список команд\n /list - посмотреть список запланированных групп психологической помощи.\n"
    update.message.reply_text(help_message)

def whoami(update, context):
    """Sends a message when the command /help is issued."""
    response = str(update.message.chat.id) + " " + \
               str(update.message.chat.username) + " " + \
               str(update.message.chat.first_name) + " " + \
               str(update.message.chat.last_name)
    update.message.reply_text(text=response)

def startCommand(update: Update, context: CallbackContext):
    start_message = f"Здравствуйте! Это бот команды @helpwithoutprejudice. Мы оказываем психологическую поддержку всем, кому нелегко в нынешнее время.\n" \
                    f"С помощью этого бота Вы сможете посмотреть список групп психологической поддержки, создать напоминание, записаться в группу, отправить донат и запросить краткосрочную терапию с одним из наших терапевтов-волонтеров.\n" \
                    f"Вот список команд, которые понимает наш бот:\n /start - начать работу с ботом\n /help - посмотреть список команд\n /list - посмотреть список запланированных групп психологической помощи.\n"
    buttons = [[InlineKeyboardButton("Список групп", callback_data="groupList")]]
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text=start_message)

def messageHandler(update: Update, context: CallbackContext):
    global session_list_dic
    global admin_cids
    cid = update.effective_chat.id
    msg = update.message.text

    if cid in session_list_dic['crisis']['members']:
        del session_list_dic['crisis']['members'][cid]
        buttons = [[InlineKeyboardButton("Список групп", callback_data="groupList")]]
        context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="Спасибо. Наш терапевт свяжется с Вами.")

        for v in admin_cids:
            context.bot.send_message(chat_id=v,
                             text=f"У нас есть заявка на кризисную терапию.\n"
                              f"От: {update.effective_chat.first_name} {update.effective_chat.last_name} @{update.effective_chat.username}\n"
                              f"Запрос: {msg}")

def queryHandler(update: Update, context: CallbackContext):
    query = update.callback_query.data
    update.callback_query.answer()
    global session_list_dic

    yoomoney_token = "4100117805460248.11EA3C4E3C9C83223569E5AC97BB3021B91BF3223716AF874F39B444D9FC3BD60D5D0EA790F537779AF123D171566090201CCEB73D2B956B925E2E7C95F7CD781C7894BF3C7549CB55D93FCD6E7AEB36F86AFBCE9747845968DB0D6794A548702838EB302925667B83BA85CFBC1F6234EB89C99BECBD15EF60CBB265D7BFFCEB"
    client = Client(yoomoney_token)

    if "groupList" == query:
        buttons = []
        for key in session_list_dic.keys():
            buttons.append([InlineKeyboardButton(session_list_dic[key]['name'], callback_data=key)])
        context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="Список групп:")

    if query in set(session_list_dic.keys()):
        session_item = session_list_dic[query]
        session_info = f"<b>{session_item['name']}</b>\n\n<b>Время</b>: {str(session_item['date_time'])}\n<b>Ведущий терапевт</b>: {session_item['specialist']}\n<b>Аннотация</b>:\n{session_item['description']}"
        label = str(query)+'_'+str(update.effective_chat.id)

        if query == "crisis":
            session_list_dic['crisis']['members'][update.effective_chat.id] = {'chat_id':update.effective_chat.id,'first_name':update.effective_chat.first_name,'last_name':update.effective_chat.last_name,'user_name':update.effective_chat.username, 'date_time': datetime.now()}
            context.bot.send_message(chat_id=update.effective_chat.id, text="Опишите свою проблему в одном сообщении. Это поможет нам подобрать терапевта для Вас.", parse_mode='html')

        elif(session_item['opengroup'] == "1"):
            session_info = session_info + f"\n\n<b>Ссылка для подключения:</b>\n{session_item['invite']}"
            buttons = [[InlineKeyboardButton("Список групп", callback_data="groupList")]]
            context.bot.send_message(chat_id=update.effective_chat.id, text=session_info, parse_mode='html', reply_markup=InlineKeyboardMarkup(buttons))

        elif((session_item['opengroup'] == "2") & (session_item['limit'] > 0) & (not update.effective_chat.id in session_item['members'].keys())):
            session_info = session_info + f"\n\nЭто <b>закрытая группа</b> с ограниченым количеством участников (осталось <b>{session_item['limit']}</b> мест). Записаться можно отправив любую предложенную сумму в качестве пожертвования.\n\n" \
                                          f"<b>Инструкция:</b>\n" \
                                          f"* нажмите на кнопку с суммой, которую хотите пожертвовать, и перейдите по ссылке\n" \
                                          f"* пожертвование можно внести с помощью карты или ЯндексКошелька\n" \
                                          f"* <b>важно:</b> после успешного перевода вернитесь в чат бота и нажмите кнопку <b>Подтвердить</b>. Так мы сможем отследить Ваш донат и прислать ссылку для подключения. Обычно это занимает несколько минут\n" \
                                          f"* если все прошло хорошо, Вы автоматически получите ссылку для подключения через бот. Если Вы не получили ссылку или получили сообщение об ошибке, свяжитесь с @kolin_drafter, мы проверим перевод вручную."

            RUR_100 = Quickpay(
            receiver="4100117805460248",
            quickpay_form="donate",
            targets="Sponsor this project",
            paymentType="SB",
            sum=10,
            label=label)

            RUR_500 = Quickpay(
                    receiver="4100117805460248",
                    quickpay_form="donate",
                    targets="Sponsor this project",
                    paymentType="SB",
                    sum=500,
                    label=label)

            RUR_1000 = Quickpay(
                    receiver="4100117805460248",
                    quickpay_form="donate",
                    targets="Sponsor this project",
                    paymentType="SB",
                    sum=1000,
                    label=label)

            buttons = [[InlineKeyboardButton("RUB 100", callback_data="rub100", url=RUR_100.redirected_url)],
                       [InlineKeyboardButton("RUB 500", callback_data="rub500", url=RUR_500.redirected_url)],
                       [InlineKeyboardButton("RUB 1000", callback_data="rub1000", url=RUR_1000.redirected_url)],
                       [InlineKeyboardButton("Подтвердить", callback_data="confirmPayment_"+query)],
                       [InlineKeyboardButton("Список групп", callback_data="groupList")]]
            context.bot.send_message(chat_id=update.effective_chat.id, text=session_info, parse_mode='html', reply_markup=InlineKeyboardMarkup(buttons))

        elif((session_item['opengroup'] == "2") & (session_item['limit'] <= 0) & (not update.effective_chat.id in session_item['members'].keys())):
            session_info = session_info + f"\n\nК сожалению, набор в это группу закрыт. Если в группе появятся места - мы пришлем уведомление."
            session_list_dic[query]['queue'][update.effective_chat.id] = {'first_name':update.effective_chat.first_name,'last_name':update.effective_chat.last_name,'user_name':update.effective_chat.username}
            buttons = [[InlineKeyboardButton("Список групп", callback_data="groupList")]]
            context.bot.send_message(update.effective_chat.id, session_info, parse_mode='html', reply_markup=InlineKeyboardMarkup(buttons))

        elif((session_item['opengroup'] == "2") & (update.effective_chat.id in session_item['members'].keys())):
            session_info = f"Вы уже записаны в эту группу. Будем ждать Вас {session_item['date_time']}.\n\nСсылка для подключения: {session_item['invite']}"
            buttons = [[InlineKeyboardButton("Список групп", callback_data="groupList")]]
            context.bot.send_message(update.effective_chat.id, session_info, parse_mode='html', reply_markup=InlineKeyboardMarkup(buttons))

        else:
            session_info = session_info + f"Хм... Что-то пошло не так...\n" \
                                          f"Попробуйте еще раз или поищите информацию в @helpwithoutprejudice. Там мы публикуем анонсы всех мероприятий."
            buttons = [[InlineKeyboardButton("Список групп", callback_data="groupList")]]
            context.bot.send_message(chat_id=update.effective_chat.id, text=session_info, parse_mode='html', reply_markup=InlineKeyboardMarkup(buttons))

    if "confirmPayment" in query:
        payment_status = False
        groupName = query.split('_')[1]
        session_item = session_list_dic[groupName]

        session_list_dic[groupName]['members'][update.effective_chat.id] = {'first_name':update.effective_chat.first_name,'last_name':update.effective_chat.last_name,'user_name':update.effective_chat.username}

        successful_donate_message = f"Мы получили Ваше пожертвование! Спасибо!\n\nСсылка для подключения к закрытой конференции:\n {session_item['invite']}\n\nБудем ждать Вас {session_item['date_time']}"
        message_to_admin = f"Пришел донат на запись в группу {session_item['name']}.\nОтправитель: {update.effective_chat.first_name} {update.effective_chat.last_name}, @{update.effective_chat.username}\nИдентификатор платежа: {groupName}_{str(update.effective_chat.id)}"
        buttons = [[InlineKeyboardButton("Список групп", callback_data="groupList")]]

        groupDate = session_item['reminder']
        dt_start = datetime.now()
        utc=pytz.UTC
        next_session = groupDate.split('_')
        next_seven_days = [datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=x) for x in range(7)]
        reminder_date = [x for x in next_seven_days if str(x.weekday()) == next_session[0]][0]
        next_session = datetime.strptime(next_session[-1],"%H:%M")
        reminder_date = reminder_date.replace(hour=next_session.hour, minute=next_session.minute, tzinfo=utc) - timedelta(days=7)

        while(not payment_status):
            history = client.operation_history(label=groupName+"_"+str(update.effective_chat.id))
            # operations = [x for x in history.operations if utc.localize(x.datetime) > reminder_date]
            operations = history.operations
            for operation in operations:
                if (operation.status == "success"):
                    context.bot.send_message(chat_id=update.effective_chat.id, text=successful_donate_message, parse_mode='html', reply_markup=InlineKeyboardMarkup(buttons))
                    payment_status = True
                else:
                    time.sleep(10)
            if ((datetime.now()-dt_start).total_seconds() > 3):
                while (update.effective_chat.id in session_list_dic[groupName]['members'].keys()):
                    del session_list_dic[groupName]['members'][update.effective_chat.id]
                context.bot.send_message(update.effective_chat.id, f"Мы не смогли подтвердить Ваш платеж. Если Вы считаете, что произошла ошибка - свяжитесь с @kolin_drafter", parse_mode='html', reply_markup=InlineKeyboardMarkup(buttons))
                break

        if(payment_status):
            session_list_dic[groupName]['limit'] -= 1
            for cid in admin_cids:
                context.bot.send_message(chat_id=cid, text=message_to_admin+f"\nВремя платежа: {operation.datetime}\nВ группе осталось <b>{session_list_dic[groupName]['limit']}</b> мест.", parse_mode='html')


def echo(update, context):
    """Echos the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Logs Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Starts the bot."""
    # Creates the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = '5423176144:AAEAHewAvanY5W4ImVC7P3RoPzlkAdzG0wA'#enter your token here
    APP_NAME='https://helpwithoutprejudice.herokuapp.com/' #Edit the heroku app-name

    # Get the dispatcher to register handlers
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", startCommand))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("whoami", whoami))
    dp.add_handler(CallbackQueryHandler(queryHandler))
    dp.add_handler(MessageHandler(Filters.text, messageHandler))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_NAME + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()