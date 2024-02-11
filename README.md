Для того, чтобы контейнеры могли подсоединиться к локальной БД 
необходимо внести следующие настройки:

1. В файле postgresql.conf изменить строку
```
listen_addresses = '*'		# what IP address(es) to listen on;
```
2. В файле pg_hba.conf добавить строки:
```commandline
host 	superset 	superset 	172.0.0.0/8 		trust
host 	huntflow_db 	superset 	172.0.0.0/8 		md5
```
3. Перезапустить постгрес:
```commandline
sudo servcie postgresql restart
```