### Запуск бота локально

```
python run.py {vk_token}
```

### Сборка докер-образа бота

```
docker build -t {tag} --build-arg VK_TOKEN={vk_token} .
```

### Запуск докер-образа бота
```
docker run --env VK_TOKEN={vk_token} {tag} 
```

### Запуск докер-образа бота в фоновом режиме

```
docker run --env VK_TOKEN={vk_token} -d -t -i {tag} 
```

### Конфиги
Для запуска бота необходим timetable_config.json
```
{
  "admins": [
    # list of admins peer_id
  ],
  "timetables": [
    {
      "description": "Timetable name",
      "all_notification": true,
      "peer_id": 0, # peer_id of target group/person
      "data_type": "google",
      "before_minutes": 5,
      "data_link": "" # link to the csv file with timetable
    }
  ]
}

```
