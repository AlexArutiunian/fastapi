```console
pip install fastapi
pip install "uvicorn[standard]"
pip install python-multipart sqlalchemy jinja2

uvicorn app:app --reload
```

# To upload on server 

1. **Необходимый Symlink**: После создания файла `myapp.service` в директории `/etc/systemd/system/`, нужно также создать символическую ссылку (symlink) в директории `/etc/systemd/system/` для этого сервиса. Это можно сделать с помощью следующей команды:
   
   ```bash
   sudo ln -s /etc/systemd/system/myapp.service /etc/systemd/system/multi-user.target.wants/myapp.service
   ```

2. **Права доступа**: Убедиться, что пользователь, указанный в секции `[Service]` вашего файла `myapp.service`, имеет необходимые права доступа к директории и файлам, необходимым для запуска FastAPI приложения.

Далее перезагрузить systemd и запустить сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
```

Если после этого сервис все еще не запускается, рекомендуется проверить журналы systemd для получения более подробной информации о возможных проблемах:

```bash
journalctl -xe
```

Чтобы FastAPI приложение продолжало работать после того, как выключится терминал или сайта сервера, следует использовать менеджер процессов, такой как `supervisord` или `systemd`.

1. **Supervisord**:
   - Установите supervisord: `sudo apt-get install supervisor`
   - Создайте конфигурационный файл для вашего приложения, например, `myapp.conf`:
     ```
     [program:myapp]
     command=uvicorn app:app --host 0.0.0.0 --port 8000
     directory=/path/to/your/app
     autostart=true
     autorestart=true
     stderr_logfile=/var/log/myapp.err.log
     stdout_logfile=/var/log/myapp.out.log
     ```
   - Запустить supervisord: `sudo service supervisor start`

2. **Systemd**:
   - Создайть systemd unit файл, например, `myapp.service` в директории `/etc/systemd/system/`:
     ```
     [Unit]
     Description=My FastAPI App
     After=network.target

     [Service]
     User=your_user
     WorkingDirectory=/path/to/your/app
     ExecStart=/usr/local/bin/uvicorn app:app --host 0.0.0.0 --port 8000
     Restart=on-failure

     [Install]
     WantedBy=multi-user.target
     ```
   - Загрузить и активировать сервис: 
     ```
     sudo systemctl daemon-reload
     sudo systemctl enable myapp
     sudo systemctl start myapp
     ```
     
Теперь FastAPI приложение будет запускаться автоматически при загрузке системы и оставаться работающим даже после закрытия терминала или выхода из сайта сервера.

