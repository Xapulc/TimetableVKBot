import pandas as pd

from loguru import logger


class Timetable(object):
    def __init__(self, timetable_json: dict):
        self._description = timetable_json["description"]
        self._data_type = timetable_json["data_type"]
        if self._data_type == "config":
            self._items = pd.DataFrame.from_records(timetable_json["data"])
        else:
            self._link = timetable_json["data_link"]

    def __str__(self):
        return self._description

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