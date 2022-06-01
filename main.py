import docx
from deep_translator import GoogleTranslator
import telebot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot import types
from telebot.storage import StateMemoryStorage
from config import *
import datetime as dt
from datetime import timedelta
import logging, os, traceback, time, wget, random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS


class EditMessage(StatesGroup):
    message_id = State()

bot = telebot.TeleBot(
                    BOT_TOKEN, 
                    state_storage = StateMemoryStorage(),
                    skip_pending=True
                    )

def __init__():
    bot.enable_save_next_step_handlers(delay=10)
    bot.load_next_step_handlers()
    bot.infinity_polling(skip_pending=True)

def bot_edit_message(chat_id, text, markup):
    try:
        with bot.retrieve_data(chat_id, chat_id) as data:
            msg = bot.edit_message_text(
                                        text, 
                                        chat_id, data["message_id"], 
                                        parse_mode="Markdown", 
                                        reply_markup=markup
                                        )
            with bot.retrieve_data(chat_id, chat_id) as data:
                data['message_id'] = msg.message_id
                
    except:
        msg = bot.send_message(
                                chat_id, 
                                text, 
                                reply_markup = markup, 
                                parse_mode="Markdown"
                            )
        bot.set_state(
                        chat_id, 
                        EditMessage.message_id, 
                        chat_id
                        )

        with bot.retrieve_data(chat_id, chat_id) as data:
            data['message_id'] = msg.message_id


@bot.message_handler(commands=['start'], chat_types="private")
def welcome_msg(message):
    bot.send_message(
                    message.chat.id, 
                    "✌️ Привет, пришли мне файл и я переведу его содержимое!"
                    )


@bot.message_handler(content_types=["document"], chat_types="private")
def get_file(message):
    try:
        file = bot.get_file(message.document.file_id)
        file_name = message.document.file_name[:10] + (message.document.file_name[10:] and '.docx')
        if file.file_size >= 300000:
            msg = bot.send_message(
                                    message.chat.id, 
                                    f"🐘 Файл \"{file_name}\" слишком большой, загрузите другой.", 
                                    parse_mode="Markdown"
                                    )
        else:
            print(f"{file_name} {file}")
            if not os.path.exists(f'{BOT_PATH}/docs/dowloads/{file_name}'):
                wget.download(
                    'https://api.telegram.org/file/bot{0}/{1}'.format(BOT_TOKEN, file.file_path), 
                                                    f'{BOT_PATH}/docs/dowloads/{file_name}', 
                                                    bar=None
                            )

            msg = bot.send_message(
                                    message.chat.id, 
                                    f"📁 Отлично, файл \"{file_name}\" загружен.", 
                                    parse_mode="Markdown"
                                    )
                                    
            kb_select_f_lang = InlineKeyboardMarkup(row_width = 2)

            kb_select_f_lang.add(
                            InlineKeyboardButton("🇷🇺 Русский", callback_data=f"SFL|{file_name}|ru"),
                            InlineKeyboardButton("🇬🇧 Английский", callback_data=f"SFL|{file_name}|en"),
                            InlineKeyboardButton("🇷🇴 Румынский", callback_data=f"SFL|{file_name}|ro"),
                            InlineKeyboardButton("🇪🇸 Испанский", callback_data=f"SFL|{file_name}|es"),
                            InlineKeyboardButton("🇺🇦 Украинский", callback_data=f"SFL|{file_name}|uk"),
                            InlineKeyboardButton("🇦🇪 Арабский", callback_data=f"SFL|{file_name}|ar"),
                            InlineKeyboardButton("🇦🇲 Армянский", callback_data=f"SFL|{file_name}|hy"),
                            InlineKeyboardButton("🇧🇬 Болгарский", callback_data=f"SFL|{file_name}|bg"),
                            InlineKeyboardButton("🇨🇿 Чешский", callback_data=f"SFL|{file_name}|cs"),
                            InlineKeyboardButton("🇪🇪 Эстонский", callback_data=f"SFL|{file_name}|et"),
                            InlineKeyboardButton("🇫🇷 Французский", callback_data=f"SFL|{file_name}|fr"),
                            InlineKeyboardButton("🇰🇿 Казахский", callback_data=f"SFL|{file_name}|kk"),
                            InlineKeyboardButton("🇵🇱 Польский", callback_data=f"SFL|{file_name}|pl"),
                            InlineKeyboardButton("🇨🇫 Африканский", callback_data=f"SFL|{file_name}|af")
                            )
                            

            msg = bot.edit_message_text(
                                        f"🌏 Выберите язык загруженного вами файла:", 
                                        message.chat.id, 
                                        msg.message_id, 
                                        reply_markup = kb_select_f_lang
                                        )

            bot.set_state(
                        message.chat.id, 
                        EditMessage.message_id, 
                        message.chat.id
                        )
            with bot.retrieve_data(message.chat.id, message.chat.id) as data:
                data['message_id'] = msg.message_id

    except Exception as error:
        traceback.print_exc()
        bot.send_message(
                        message.chat.id, 
                        f"☹️ Мне не удалось открыть ваш файл, загрузите другой.", 
                        parse_mode="Markdown"
                        )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    valid_lang = ["ru", "en", "ro", "es", "uk", "ar", "hy", "bg", "cs", "et", "fr", "kk", "pl", "af"]
    zdata = (call.data).split("|")
    if zdata[0] == "SFL":
        if zdata[2] in valid_lang:

            kb_select_f_lang = InlineKeyboardMarkup(row_width = 1)

            kb_select_f_lang.add(
                                InlineKeyboardButton("🇷🇺 Русский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|ru"),
                                InlineKeyboardButton("🇬🇧 Английский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|en"),
                                InlineKeyboardButton("🇷🇴 Румынский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|ro"),
                                InlineKeyboardButton("🇪🇸 Испанский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|es"),
                                InlineKeyboardButton("🇺🇦 Украинский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|uk"),
                                InlineKeyboardButton("🇦🇪 Арабский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|ar"),
                                InlineKeyboardButton("🇦🇲 Армянский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|hy"),
                                InlineKeyboardButton("🇧🇬 Болгарский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|bg"),
                                InlineKeyboardButton("🇨🇿 Чешский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|cs"),
                                InlineKeyboardButton("🇪🇪 Эстонский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|et"),
                                InlineKeyboardButton("🇫🇷 Французский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|fr"),
                                InlineKeyboardButton("🇰🇿 Казахский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|kk"),
                                InlineKeyboardButton("🇵🇱 Польский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|pl"),
                                InlineKeyboardButton("🇨🇫 Африканский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|af")
                                )

            bot_edit_message(
                            call.message.chat.id, 
                            f"🌍 Выберите язык на который нужно перевести файл", 
                            kb_select_f_lang
                            )

        else:
            bot_edit_message(
                            call.message.chat.id, 
                            f"😌 Данный языковой пакет не доступен, выберите другой.",
                            None
                            )

    elif zdata[0] == "TRANSLETE":
        try:
            bot_edit_message(
                            call.message.chat.id, 
                            f"⏳ Перевожу файл, это может занять некоторое время ... ",
                            None
                            )

            doc = docx.Document(f'{BOT_PATH}/docs/dowloads/{zdata[1]}')
            out_txt_name = zdata[1].replace(".docx", ".txt")
            
            with open(f'{BOT_PATH}/docs/results/{out_txt_name}', "w", encoding="utf-8") as txt_result:
                for paragraph in doc.paragraphs:
                    transleted_text = GoogleTranslator(source = zdata[2], target=zdata[3]).translate(paragraph.text)

                    txt_result.write(f"\n{transleted_text}")

                    if paragraph.text.find(paragraph.text) >= 0:
                        paragraph.text = paragraph.text.replace(paragraph.text, transleted_text)

                    print(transleted_text)

            txt_result.close()
            doc.save(f'{BOT_PATH}/docs/results/{zdata[1]}')

            kb = InlineKeyboardMarkup(row_width = 1)
            kb.add(
                InlineKeyboardButton("🖊️ Получить в виде текста", callback_data=f"GET-RESULT|TEXT|{out_txt_name}"),
                InlineKeyboardButton("📕 Получить в виде DOCX файла", callback_data=f"GET-RESULT|DOCX|{zdata[1]}"),
                InlineKeyboardButton("📃 Получить в виде TXT файла", callback_data=f"GET-RESULT|TXT|{out_txt_name}"),
                InlineKeyboardButton("🔊 Озвучить текст", callback_data=f"GET-RESULT|VOICE|{out_txt_name}|{zdata[3]}")
                )

            bot_edit_message(
                            call.message.chat.id, 
                            f"👍 Файл переведен, выберите в каком виде хотите получить результат:", 
                            kb
                            )

        except Exception as error:
            print(error)
            traceback.print_exc()
            bot_edit_message(
                            call.message.chat.id, 
                            f"⚠ Возникла ошибка при переводе, повторите попытку!\n🌍 Возможно вы указали неверный язык файла"
                            , None
                            )

    elif zdata[0] == "GET-RESULT":
        if zdata[1] == "TEXT":
            try:

                text = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "r")
                bot.send_message(
                                call.message.chat.id, 
                                text.read()
                                )
                text.close()

            except:
                bot.send_message(
                                call.message.chat.id,
                                "🐘 Файл слишком большой, откройте его другим способом"
                                )
        

        elif zdata[1] == "TXT":
            doc = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "rb")
            bot.send_document(call.message.chat.id, doc)
            doc.close()

        elif zdata[1] == "DOCX":
            doc = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "rb")
            bot.send_document(call.message.chat.id, doc)

        elif zdata[1] == "VOICE":
            try:
                text = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "r", encoding="utf-8")
                voice_message = gTTS(text = text.read(), lang=f"{zdata[3]}", slow=False)
                name = f"{call.message.chat.id}_{random.randint(0, 99)}.ogg"
                voice_message.save(name)
                voice = open(name, 'rb')
                bot.send_voice(call.message.chat.id, voice)
                voice.close()
                text.close()
                os.remove(name)
            
            except:
                bot.send_message(
                                call.message.chat.id,
                                "🐘 Файл слишком большой, откройте его другим способом"
                                )



if __name__ == "__main__":
    __init__()