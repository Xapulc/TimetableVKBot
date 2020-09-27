import asyncio
import json
import numpy as np
from loguru import logger

from vkbottle import Bot, Message
from vkbottle.api.keyboard import Keyboard, Text

from Timetable import Timetable


class TimetableBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open("timetable_config.json", "r") as timetable_file:
            self._timetables = {timetable_json.pop("peer_id"): Timetable(timetable_json)
                                for timetable_json in json.load(timetable_file)}

    def _generate_keyboard(self) -> str:
        keyboard = Keyboard()
        keyboard.add_row()
        keyboard.add_button(Text("Запустить автоуведомления."), color="positive")
        keyboard.add_row()
        keyboard.add_button(Text("Да или нет?"), color="primary")
        keyboard.add_row()
        keyboard.add_button(Text("Поддержать."))
        return keyboard.generate()

    async def get_answer(self, ans: Message, message: str, chat_flg: bool = None):
        logger.info(ans)
        if message == "" or message == ".":
            await ans("Привет! 😊", keyboard=self._generate_keyboard())
        elif message == "/get_peer_id":
            await ans(f"peer_id = {ans.peer_id}")
        elif message == "Запустить автоуведомления.":
            if ans.peer_id in self._timetables.keys():
                timetable = self._timetables[ans.peer_id]
                await ans(f"Расписание \"{timetable}\" найдено.\n"
                          + f"Буду уведомлять вас за {timetable.get_before_minutes()} минут(ы) до начала занятия.")

                while True:
                    messages = timetable.make_notifications()
                    for message in messages:
                        await ans(message)
                    if len(messages) > 0:
                        await asyncio.sleep(120)
                    else:
                        await asyncio.sleep(15)
            else:
                await ans("Извините, я не знаю подходящего расписания для нашей беседы.\n"
                          + "Обратитесь к запустившему меня, чтобы тот добавил ваше расписание в конфиг.")
        elif message == "Да или нет?":
            await ans(np.random.choice(["Да", "Нет"], 1)[0])
        elif message == "Поддержать.":
            await ans("Спасибо! Ссылка на проект: https://github.com/Xapulc/TimetableVKBot.")
        else:
            await ans("Не знаю что вам ответить.")