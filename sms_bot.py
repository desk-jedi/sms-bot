#
# ---------------------------------------------------------------------------
#                      Скрипт бота для пересылки СМС
#                           Автор: Антон Степанов
#                          Версия: 1.04 (ProxyLab)
#                             Дата: 2024-12-05
# ---------------------------------------------------------------------------
# Описание:
#    Этот скрипт предназначен для управления Telegram-ботом, который
#    пересылает СМС из группы 'Общий канал СМС', находящейся под контролем
#    бота в приложении Remote Bot.
# ---------------------------------------------------------------------------
#


import telebot

"""
Код позволяет загружать токен бота из файла, обрабатывает случай отсутствия файла 
и создает объект бота для дальнейшей работы.
Токен принадлежит номеру QIWI1.

Исключение FileNotFoundError обрабатывается, чтобы проверить наличие конфигурационного файла.
Если файл не найден, выводится сообщение об ошибке.
"""

try:
    with open("token.conf", "r", encoding="utf-8") as token_file:
        token = token_file.read()
    with open("token.conf.backup", "w", encoding="utf-8") as token_backup_file:
        token_backup_file.write(token)
except FileNotFoundError:
    print("Файл token.conf не найден.")
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start(message, res=False):
    """
    Функция @bot.message_handler отвечает на команду `/start`, приветствует пользователя
    и дает ему информацию о том, как получить справку о работе бота.
    """
    bot.send_message(
        message.chat.id,
        f"Привет, <b>{message.from_user.first_name}</b>. Я предназначен для рассылки СМС🤖",
        parse_mode="html",
    )
    bot.send_message(
        message.chat.id,
        "Чтобы ознакомиться с работой со мной, обратитесь за справкой в <b>Notion</b>",
        parse_mode="html",
    )


@bot.message_handler(content_types=["text"])
def handle_text(message):
    """
    Функция @bot.message_handler позволяет обрабатывать текстовые сообщения,
    пересылать их в указанные чаты на основании настроек в файле конфигурации
    и добавлять новые настройки.

    Обрабатываются и исключения, чтобы информировать пользователя
    о проблемах с файлом конфигурации.
    Если файл не найден, пользователю отправляется соответствующее сообщение.
    """
    try:
        with open("settings.conf", "r", encoding="utf-8") as conf:
            chat_id = []
            filters = []

            for line in conf:
                line = line.strip()
                pos = line.find(":")

                if pos != -1:
                    chat_id.append(line[:pos])
                    filters.append(line[pos + 1 :])
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "❗️Файл <b>`settings.conf`</b> не найден",
            parse_mode="html",
        )
    for i, chat in enumerate(chat_id):
        if filters[i] in message.text:
            try:
                bot.send_message(chat, message.text)
            except Exception:
                print(f"Чат с идентификатором {chat} не найден")
    if (
        (message.text.find(":") != -1)
        and (message.text[-1] != ":")
        and (message.text.find("Пришло СМС") == -1)
        and (message.text.find("Пропущенный вызов") == -1)
    ):
        try:
            with open("settings.conf", "a+", encoding="utf-8") as conf:
                conf.write("\n" + message.text)
                conf.seek(0)

                with open(
                    "settings.conf.backup", "w", encoding="utf-8"
                ) as settings_backup:
                    settings_backup.writelines(conf.readlines())
            bot.send_message(message.chat.id, "✅Настройка успешно применена")
        except FileNotFoundError:
            bot.send_message(
                message.chat.id,
                "❗️Файл <b>`settings.conf`</b> не найден",
                parse_mode="html",
            )
    elif message.text[-1] == ":":
        bot.send_message(message.chat.id, "❗️Некорректный вид команды")


"""
Запуск бота в работу, опрос сервера для получения новых сообщений.
Параметры none_stop и interval контролируют постоянство работы и задержку между запросами.
"""
bot.polling(none_stop=True, interval=0)
