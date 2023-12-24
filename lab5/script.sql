SELECT * FROM applications

DELETE FROM applications WHERE application_id=3

SELECT * FROM applications_actions

DELETE FROM applications_actions WHERE application_id=3

INSERT INTO applications VALUES (4, 'проверяется', '2003-08-10 04:00:00+04', '2003-08-11 04:00:00+04', '2003-08-13 04:00:00+04', 1, 1)

INSERT INTO applications VALUES (5, 'зарегистрирован', '2003-08-10 04:00:00+04', '2003-08-11 04:00:00+04', '2003-08-13 04:00:00+04', 1, 1)