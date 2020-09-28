import argparse
import json
import re

from vkbottle import Message

from Bot import TimetableBot
from Timetable import Timetable

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Бот в ВК для уведомления о расписании")
    parser.add_argument('token', metavar='T', type=str, help='токен бота')
    token = parser.parse_args().token

    bot = TimetableBot(token)
    before_minutes = 5
    timetable = None
    timetable_keyboard = None

    @bot.on.chat_message()
    async def wrapper(ans: Message):
        message_texts = re.findall(r"^\[club{0}\|[^\]]+\](.*)".format(bot.group_id), ans.text)
        if len(message_texts) > 0:
            message_text = message_texts[0].strip()
            await bot.get_answer(ans, message_text, chat_flg=True)

    @bot.on.message()
    async def wrapper(ans: Message):
        message_text = ans.text
        await bot.get_answer(ans, message_text, chat_flg=False)

    bot.run_polling()
