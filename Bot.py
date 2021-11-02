import asyncio
import json
import os

import numpy as np
from loguru import logger
from urllib.error import URLError

from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor

from Timetable import Timetable


class TimetableBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(task_each_event=True, *args, **kwargs)
        config_path = "timetable_config.json"

        assert os.path.exists(config_path), f"Config file {config_path} not found."
        with open(config_path, "r") as timetable_file:
            timetables_json = json.load(timetable_file)
            self._admins = timetables_json["admins"]
            self._timetables = {timetable.pop("peer_id"): Timetable(timetable)
                                for timetable in timetables_json["timetables"]}
            self._timetable_work_flg = False

    def _generate_keyboard(self, peer_id, chat_flg=False) -> str:
        admin_flg = peer_id in self._admins
        keyboard = Keyboard(one_time=not admin_flg and chat_flg)
        if not self._timetable_work_flg and admin_flg:
            keyboard.row()
            keyboard.add(Text("Включить уведомления."), color=KeyboardButtonColor.POSITIVE)
        keyboard.row()
        keyboard.add(Text("Расписание на сегодня."), color=KeyboardButtonColor.POSITIVE)
        keyboard.row()
        keyboard.add(Text("Да или нет?"), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text("Поддержать."))
        return keyboard.get_json()

    async def get_answer(self, ans: Message, message: str, chat_flg: bool = None):
        logger.info(ans)
        if message.lower() in ["", ".", ",", "привет"]:
            await ans.answer("Привет! 😊", keyboard=self._generate_keyboard(ans.peer_id, chat_flg))
        elif message == "/get_peer_id":
            await ans.answer(f"peer_id = {ans.peer_id}")
        elif message == "Включить уведомления.":
            if ans.from_id in self._admins:
                if not self._timetable_work_flg:
                    self._timetable_work_flg = True
                    await ans.answer("Привет. Следующие расписания будут запущены:\n"
                                     + "\n".join("📅 " + str(timetable) for timetable in self._timetables.values()),
                                     keyboard=self._generate_keyboard(ans.peer_id, chat_flg))

                    while True:
                        messages_flg = False
                        for peer_id, timetable in self._timetables.items():
                            answer, err = timetable.make_notification(time="now")
                            if err is not None:
                                for admin in self._admins:
                                    msg = f"""
                                    Нотификация к peer_id={peer_id} по расписанию "{timetable.get_description()}" 
                                    завершилась с ошибкой: {err}
                                    """
                                    try:
                                        await self.api.messages.send(message=msg, peer_id=admin, random_id=0)
                                    except Exception as e:
                                        logger.error(e)
                                        logger.error(f"Message = {answer}")
                                        messages_flg = False
                            if answer is not None:
                                messages_flg = True
                                try:
                                    await self.api.messages.send(message=answer, peer_id=peer_id, random_id=0)
                                except Exception as e:
                                    logger.error(e)
                                    logger.error(f"Message = {answer}")
                                    messages_flg = False

                        if messages_flg:
                            await asyncio.sleep(120)
                        else:
                            await asyncio.sleep(15)
                else:
                    await ans.answer("Уведомления уже запущены.")
            else:
                await ans.answer("Извините, но вы не можете воспользоваться этой командой.")
        elif message == "Расписание на сегодня.":
            if ans.peer_id in self._timetables.keys():
                answer, err = self._timetables[ans.peer_id].make_notification(time="today")
                if err is not None:
                    answer = f"""
                              Нотификация завершилась с ошибкой: {err}
                              """
                if answer is None:
                    answer = "Извините, но я не имею доступа к вашему расписанию."
                await self.api.messages.send(message=answer, peer_id=ans.peer_id, random_id=0)

            else:
                await ans.answer("К сожалению, для вашей беседы у меня нет расписания.")
        elif message == "Да или нет?":
            await ans.answer(np.random.choice(["Да", "Нет"], 1)[0])
        elif message == "Поддержать.":
            await ans.answer("Спасибо! Ссылка на проект: https://github.com/Xapulc/TimetableVKBot.")
        else:
            await ans.answer("Не знаю что вам ответить.")
