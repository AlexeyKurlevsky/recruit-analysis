В проекте используется Python 3.10. Запуск проекта:
```commandline
sh ./bin/start_project.sh
```
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

Генерация FERNET CODE
```python
from cryptography.fernet import Fernet

fernet_key = Fernet.generate_key()
print(fernet_key.decode())
```

Экспорт realm из keycloak
```commandline
docker exec -it recruit-analisys-keycloak-1 /opt/keycloak/bin/kc.sh export --dir /opt/keycloak/data --realm alkurlevsky --users realm_file
```