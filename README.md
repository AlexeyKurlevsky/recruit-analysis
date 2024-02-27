Для того, чтобы контейнеры могли подсоединиться к локальной БД 
необходимо внести следующие настройки:

1. В файле postgresql.conf изменить строку
```
listen_addresses = '*'		# what IP address(es) to listen on;
```
2. В файле pg_hba.conf добавить строки:
```commandline
host 	superset 	superset 	172.0.0.0/8 		scram-sha-256
host    superset        superset        192.168.0.0/16        	scram-sha-256
host 	huntflow_db 	superset 	172.0.0.0/8 		scram-sha-256
host 	huntflow_db 	superset 	192.168.0.0/16 		scram-sha-256
```
3. Перезапустить постгрес:
```commandline
sudo servcie postgresql restart
```

Генерация AIRFLOW_SECRET_KEY
```commandline
openssl rand -base64 32
```