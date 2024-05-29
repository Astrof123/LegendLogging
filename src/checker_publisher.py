with open("tmp/publisher.log", "r") as f:
    logs = f.readlines()
    phrases = ["Издатель получил id", "Издатель запустил приложение с id",
               "Подключение к брокеру", "Будет", "Идет публикация по теме",
               "Отправлено сообщение", "Публикация закончена"]
    ids = []

    def findError(user_id):
        flag = False
        k = 0
        for line in logs:
            if not(flag) and user_id in line and (phrases[0] in line or phrases[1] in line):
                flag = True
                k += 2
                continue

            if not(flag) and user_id in line:
                print(f"Неправильно -> {line}")
                print(f"Должен быть лог: \"{phrases[k]}...\"")
                print("Сообщения появляются не в правильном порядке")
                exit()


            if flag and user_id in line:
                if phrases[k] == "Отправлено сообщение":
                    if phrases[-1] in line:
                        k = 0
                        flag = False
                        continue
                    else:
                        continue

                if phrases[k] in line:
                    k += 1
                    continue
                else:
                    print(f"Неправильно -> {line}")
                    print(f"Должен быть лог: \"{phrases[k]}...\"")
                    print("Сообщения появляются не в правильном порядке")
                    exit()


    for line in logs:

        if phrases[0] in line or phrases[1] in line:
            user_id = line.split(":")[-1].strip()
            if user_id not in ids:
                ids.append(user_id)
        elif len(line) != 1:
            try:
                user_id = line.split("—")[-2].split(":")[1].strip()
            except IndexError:
                continue

            if user_id not in ids:
                ids.append(user_id)


    for user_id in ids:
        findError(user_id)

    print("Сообщения появляются в правильном порядке")




