import argparse
import asyncio
import json
import numpy as np

from loguru import logger
from vkbottle import Bot, Message

from Timetable import Timetable

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Бот в ВК для уведомления о расписании")
    parser.add_argument('token', metavar='T', type=str, help='токен бота')
    token = parser.parse_args().token
    bot = Bot(token)
    before_minutes = 5

    with open("timetable_config.json", "r") as timetable_file:
        timetables = {timetable_json.pop("peer_id"): Timetable(timetable_json)
                      for timetable_json in json.load(timetable_file)}

    @bot.on.message_handler(text="Да или нет?")
    async def wrapper(ans: Message):
        await ans(np.random.choice(["Да", "Нет"], 1)[0])

    @bot.on.message_handler(text="/get_peer_id")
    async def wrapper(ans: Message):
        await ans(f"peer_id = {ans.peer_id}")

    @bot.on.message_handler(text='/timetable_start')
    async def wrapper(ans: Message):
        logger.info(ans)
        await ans(f"Привет, @id{ans.from_id}(землянин)")
        if ans.peer_id in timetables.keys():
            timetable = timetables[ans.peer_id]
            await ans(f"Расписание \"{timetable}\" найдено.\n"
                      + f"Буду уведомлять вас за {before_minutes} минут(ы) до начала занятия.")

            while True:
                messages = timetable.make_notifications(before_minutes)
                for message in messages:
                    await ans(message)
                if len(messages) > 0:
                    await asyncio.sleep(120)
                else:
                    await asyncio.sleep(15)
        else:
            await ans("Извините, я не знаю подходящего расписания для нашей беседы.\n"
                      + "Обратитесь к запустившему меня, чтобы тот добавил ваше расписание в конфиг.")

    bot.run_polling()
