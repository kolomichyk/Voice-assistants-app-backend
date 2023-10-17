import psycopg2

conn = psycopg2.connect(dbname="rip2", user="lab2", password="lab2", port="8081")

cursor = conn.cursor()
 
cursor.execute("INSERT INTO actions (id, title, description, img, status) VALUES(1, 'Узнать погоду', 'Просто скажите :\" Узнать погоду в...\"', 'img/1.jpg', 0)")
cursor.execute("INSERT INTO actions (id, title, description, img, status) VALUES(2, 'Поставить будильник', 'Просто скажите :\" Поставь будильник на...\"', 'img/2.jpg', 0)")
cursor.execute("INSERT INTO actions (id, title, description, img, status) VALUES(3, 'Включить музыку', 'Просто скажите :\" Включи музыку или вкулючи каку-то песню\"', 'img/3.jpg', 0)")
cursor.execute("INSERT INTO actions (id, title, description, img, status) VALUES(4, 'Записать заметку', 'Просто скажите :\" Запиши в заметки...\"', 'img/4.jpg', 0)")
conn.commit()   # реальное выполнение команд sql1
 
cursor.close()
conn.close()