# birbs


```
sudo apt-get install libpq-dev
sudo apt-get install python3-psycopg2
```


# todo:

- fastapi_users сделать аутентификацию:
  - развернуть postgress бд
- завернуть api в контейнер:
  - https://github.com/avishayp/spidev
  - https://github.com/hypriot/rpi-kernel/issues/24
  - ``` docker run --rm -it --cap-add ALL -v /lib/modules:/lib/modules -v /sys:/sys --device /dev/ttyAMA0:/dev/ttyAMA0 --device /dev/mem:/dev/mem --privileged  --entrypoint bash ubuntu:18.04```
- фоновый процесс который по расписанию работает
- крутую ui для настройки всяких штук
- логгирование информации через телеграм бота