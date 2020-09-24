import argparse
import re
import json
import time
import pandas as pd

from loguru import logger
from vkbottle import Bot, Message
from vkbottle.keyboard import Keyboard, Text


class Timetable(object):
    def __init__(self, timetable_json: dict):
        self._data_type = timetable_json["data_type"]
        if self._data_type == "config":
            self._items = pd.DataFrame.from_records(timetable_json["data"])
        else:
            self._link = timetable_json["data_link"]

    def _get_record_on_time(self, data: pd.DataFrame, before_minutes: int) -> pd.DataFrame:
        week_day = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"
        ]
        time_of_notification = pd.Timestamp("now") + pd.Timedelta(minutes=before_minutes)
        logger.info(time_of_notification)
        return data.loc[data["День недели"] == week_day[time_of_notification.weekday()]] \
                   .loc[(data["Периодичность"] == "Всегда")
                        | (data["Периодичность"] == "Нечётная" if time_of_notification.week % 2 else "Чётная")] \
                   # .loc[data["Начало пары"] == time_of_notification.strftime("%H:%M")]

    def make_notifications(self, before_minutes: int = 5):
        if self._data_type == "config":
            data = self._get_record_on_time(self._items, before_minutes)
        else:
            data = self._get_record_on_time(pd.read_csv(self._link), before_minutes)
        notifications = []
        for index, row in data.iterrows():
            notifications.append(f"""{row["Тип пары"]} по предмету "{row["Предмет"]}" начинается в {row["Начало пары"]}.\n"""
                                 + f"""Расположение: {row["Расположение"]}.""")
        return notifications


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Бот в ВК для уведомления о расписании")
    parser.add_argument('token', metavar='T', type=str, help='токен бота')
    token = parser.parse_args().token
    bot = Bot(token)
    before_minutes = 5

    with open("timetable_config.json", "r") as timetable_file:
        timetables = {timetable_name: Timetable(timetable_json)
                      for timetable_name, timetable_json in json.load(timetable_file).items()}

    keyboard = Keyboard(one_time=True)
    for timetable in timetables.keys():
        keyboard.add_row()
        keyboard.add_button(Text(label=timetable), color="primary")

    @bot.on.message()
    async def wrapper(ans: Message):
        await ans(f"Привет. К сожалению, я работаю только в беседах.")

    @bot.on.chat_message(text='/bot_start', lower=True)
    async def wrapper(ans: Message):
        await ans(f"Привет, @id{ans.from_id}(землянин)")
        await ans(f"Выберите, пожалуйста, согласно какому расписанию вы хотите получать уведомления.",
                  keyboard=keyboard.generate())

    @bot.on.chat_message()
    async def wrapper(ans: Message):
        timetable_name_re = re.findall(r"^\[club{0}\|@public{0}\] (.+)".format(bot.group_id), ans.text)
        if len(timetable_name_re) > 0:
            timetable_name = timetable_name_re[0]
            if timetable_name in timetables.keys():
                timetable = timetables[timetable_name]
                await ans("Расписание найдено!\n"
                          + f"Буду уведомлять вас за {before_minutes} минут(ы) до начала занятия.")

                while True:
                    messages = timetable.make_notifications(before_minutes)
                    for message in messages:
                        await ans(message)
                    if len(messages) > 0:
                        time.sleep(120)
                    else:
                        time.sleep(15)
            else:
                message = f"Вашего расписания {timetable_name} нет в списке доступных.\n" \
                          + "Напишите /bot_start, чтобы выбрать подходящее расписание."
                await ans(message)

    bot.run_polling()
