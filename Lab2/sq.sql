SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public';

GRANT CONNECT ON DATABASE rip2 TO lab2;
   
GRANT ALL PRIVILEGES ON SCHEMA public TO lab2;
   

CREATE TABLE TMP(
	sad serial
)

DROP TABLE TMP

SELECT * FROM voice_helper_goods

DELETE FROM voice_helper_goods WHERE id = 1

CREATE DATABASE rip2 OWNER lab2

DROP DATABASE rip2