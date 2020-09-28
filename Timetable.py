import pandas as pd

from loguru import logger


class Timetable(object):
    def __init__(self, timetable_json: dict):
        self._description = timetable_json["description"]
        self._data_type = timetable_json["data_type"]
        self._before_minutes = timetable_json.get("before_minutes", 5)
        self._all_notification_flg = timetable_json.get("all_notification", False)
        if self._data_type == "config":
            self._items = pd.DataFrame.from_records(timetable_json["data"])
        else:
            self._link = timetable_json["data_link"]

    def __str__(self):
        return self._description

    def get_before_minutes(self):
        return self._before_minutes

    def _get_record_on_time(self, data: pd.DataFrame, time="now") -> pd.DataFrame:
        week_day = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"
        ]
        time_of_notification = pd.Timestamp("now") + pd.Timedelta(minutes=self._before_minutes) if time == "now" \
                               else pd.Timestamp("now")

        return_data = data.loc[data["День недели"] == week_day[time_of_notification.weekday()]] \
                          .loc[(data["Периодичность"] == "Всегда")
                               | (data["Периодичность"] == ("Нечётная" if time_of_notification.week % 2 else "Чётная"))]
        if time == "now":
            return return_data.loc[data["Начало пары"] == time_of_notification.strftime("%H:%M")]
        else:
            return return_data

    def make_notification(self, time="now"):
        if self._data_type == "config":
            data = self._get_record_on_time(self._items, time)
        else:
            data = self._get_record_on_time(pd.read_csv(self._link), time)
        notifications = []
        for index, row in data.iterrows():
            notification = f"""{row["Тип пары"]} по предмету "{row["Предмет"]}".\n""" \
                           + f"""⏱ {row["Начало пары"]} - {row["Конец пары"]}\n""" \
                           + f"""Расположение: {row["Расположение"]}."""
            notifications.append(notification)
        if time == "now":
            if len(notifications) > 0:
                return ("@all \n" if self._all_notification_flg else "") + "\n\n".join(notifications)
            else:
                return None
        else:
            if len(notifications) == 0:
                return "Сегодня нет пар."
            else:
                return f"Сегодня {'одна пара' if len(notifications) == 1 else f'{len(notifications)} пар'}.\n\n" \
                       + "\n\n".join(notifications)
