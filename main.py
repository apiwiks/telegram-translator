import docx
from deep_translator import GoogleTranslator
import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from config import *
import datetime as dt
import logging, os, traceback, wget, random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS


class EditMessage(StatesGroup): # Класс для сохранение ID сообщения
    message_id = State()

bot = telebot.TeleBot(
                    BOT_TOKEN, # Токен бота из config.py
                    state_storage = StateMemoryStorage(), # Сохранение данных бота при перезагрузке
                    skip_pending=True
                    )

logging.basicConfig(filename = "loggs.log", # Логгирование событий в файл loggs.log
                format=f"%(levelname)s: {dt.datetime.now().strftime('%d.%m %H:%M')} %(message)s",
                level=logging.INFO)


def __init__(): # Функция стартер

    print(f"Bot started")

    logging.info("Bot started")

    bot.enable_save_next_step_handlers(delay=10)

    bot.load_next_step_handlers()

    bot.infinity_polling(skip_pending=True)


def bot_edit_message(chat_id, text, markup): # Редактирование сообщений от бота
    try:
        with bot.retrieve_data(chat_id, chat_id) as data: # Получение ID сообщения
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


@bot.message_handler(commands=['start'], chat_types="private") # Функция обработки команды /start
def welcome_msg(message):
    bot.send_message(
                    message.chat.id, 
                    "✌️ Привет, пришли мне файл и я переведу его содержимое!"
                    )
    logging.info(f"{message.chat.id} > /start") # Запись логов в журнал


@bot.message_handler(content_types=["document"], chat_types="private") # Срабатывает при получении файла от пользователя
def get_file(message):
    try:
        file = bot.get_file(message.document.file_id) # Получение информции о файле
        print(message.document.file_name[-5:])
        if message.document.file_name[-5:] == ".docx" or message.document.file_name[-5:] == ".DOCX": # Проверка формата файла
            file_name = message.document.file_name[:10] + (message.document.file_name[10:] and '.docx')
            if file.file_size >= 300000: # Проверка размера файла
                logging.error(f"{message.chat.id} upload big size file")
                msg = bot.send_message(
                                        message.chat.id, 
                                        f"🐘 Файл \"{file_name}\" слишком большой, загрузите другой.", 
                                        parse_mode="Markdown"
                                        )
            else:
                print(f"{file_name} {file}")
                if not os.path.exists(f'{BOT_PATH}/docs/dowloads/{file_name}'): # Если файла нет в директории
                    wget.download(                                              # Начинай скачивание в директорию
                        'https://api.telegram.org/file/bot{0}/{1}'.format(BOT_TOKEN, file.file_path), 
                                                        f'{BOT_PATH}/docs/dowloads/{file_name}', 
                                                        bar=None
                                )

                msg = bot.send_message(
                                        message.chat.id, 
                                        f"📁 Отлично, файл \"{file_name}\" загружен.", 
                                        parse_mode="Markdown"
                                        )
                                        
                kb_select_f_lang = InlineKeyboardMarkup(row_width = 2) # Клавиатура выбора языка

                kb_select_f_lang.add(
                                InlineKeyboardButton("🇷🇺 Русский", callback_data=f"SFL|{file_name}|ru"), # ТЕКСТ КНОПКИ \ Текстовая дата кнопки
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

                bot.set_state(              # установка шага пользователя
                            message.chat.id, 
                            EditMessage.message_id, 
                            message.chat.id
                            )
                with bot.retrieve_data(message.chat.id, message.chat.id) as data:
                    data['message_id'] = msg.message_id

                logging.info(f"{message.chat.id} upload file {file_name}")

        else:
            bot.send_message(
                            message.chat.id, 
                            f"☹️ Данный формат файла не поддерживается, загрузите .docx", 
                            parse_mode="Markdown"
                            )

    except Exception as error:
        traceback.print_exc()
        logging.error(f"{message.chat.id} Error FILE: {error}")
        bot.send_message(
                        message.chat.id, 
                        f"☹️ Мне не удалось открыть ваш файл, загрузите другой.", 
                        parse_mode="Markdown"
                        )


@bot.callback_query_handler(func=lambda call: True) # Срабатывает при нажатии на Inline клавиатуру бота
def callback_query(call):
    valid_lang = ["ru", "en", "ro", "es", "uk", "ar", "hy", "bg", "cs", "et", "fr", "kk", "pl", "af"] # Список кодов допустимых языков
    logging.info(f"{call.message.chat.id} > {call.data}") 
    zdata = (call.data).split("|") # Разбиение calldata на эллементы 
    try:
        if zdata[0] == "SFL":
            if zdata[2] in valid_lang: # Если язык в списке разрешенных

                kb_select_f_lang = InlineKeyboardMarkup(row_width = 1)

                kb_select_f_lang.add(
                                    InlineKeyboardButton("🇷🇺 Русский", callback_data=f"TRANSLETE|{zdata[1]}|{zdata[2]}|ru"), # Перевод|название файла|язык1|язык2
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

                doc = docx.Document(f'{BOT_PATH}/docs/dowloads/{zdata[1]}') # Отрытие docx
                out_txt_name = zdata[1].replace(".docx", ".txt")
                
                with open(f'{BOT_PATH}/docs/results/{out_txt_name}', "w", encoding="utf-8") as txt_result: # Запись результата перевода в файлы
                    for paragraph in doc.paragraphs:
                        transleted_text = GoogleTranslator(source = zdata[2], target=zdata[3]).translate(paragraph.text) # Переводчик

                        txt_result.write(f"\n{transleted_text}") # Запись в txt

                        if paragraph.text.find(paragraph.text) >= 0:
                            paragraph.text = paragraph.text.replace(paragraph.text, transleted_text) # Запись в docx

                        print(transleted_text)

                txt_result.close()
                doc.save(f'{BOT_PATH}/docs/results/{zdata[1]}') # Сохранения переведенного файла docx

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

        elif zdata[0] == "GET-RESULT": # Дата вывода результатов
            if zdata[1] == "TEXT": # Если пользователь хочет вывести в виде текста
                try:

                    text = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "r") # Чтение txt и отправка текста пользователю
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
            

            elif zdata[1] == "TXT": # Если пользователь хочет вывести в виде .txt файла
                doc = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "rb")
                bot.send_document(call.message.chat.id, doc)
                doc.close()

            elif zdata[1] == "DOCX": # Если пользователь хочет вывести в виде .docx файла 
                doc = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "rb")
                bot.send_document(call.message.chat.id, doc)

            elif zdata[1] == "VOICE": # Если пользователь хочет вывести в виде голосового сообщения
                try:
                    text = open(f"{BOT_PATH}/docs/results/{zdata[2]}", "r", encoding="utf-8")
                    voice_message = gTTS(text = text.read(), lang=f"{zdata[3]}", slow=False) # Преобразование текста в речь при помощи gTTS
                    name = f"{call.message.chat.id}_{random.randint(0, 99)}.ogg" 
                    voice_message.save(name) # Сохранение .ogg файла
                    voice = open(name, 'rb')
                    bot.send_voice(call.message.chat.id, voice) # Отправка .ogg файла пользователю
                    voice.close()
                    text.close()
                    os.remove(name) # Удаление файла из директории
                
                except:
                    bot.send_message(
                                    call.message.chat.id,
                                    "🐘 Файл слишком большой, мне не удалось воспроизвести его."
                                    )

    except Exception as error:
        logging.error(f"{call.message.chat.id} ERROR CALL-BACK: {error}")
        return welcome_msg(call.message)

if __name__ == "__main__":
    __init__()