# birbs


```
sudo apt-get install libpq-dev
sudo apt-get install python3-psycopg2
```


# todo:

  + fastapi_users сделать аутентификацию:
  + развернуть postgress бд
  + завернуть api в контейнер:
    + https://github.com/avishayp/spidev
    + https://github.com/hypriot/rpi-kernel/issues/24
    + ``` docker run --rm -it --cap-add ALL -v /lib/modules:/lib/modules -v /sys:/sys --device /dev/mem:/dev/mem --privileged  --entrypoint bash ubuntu:18.04```
  - фоновый процесс который по расписанию работает
  - логгирование информации через телеграм бота
  - крутую ui для настройки всяких штук (ага щас)




# install docker
sudo apt install ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER

# install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose


# почта

https://stackoverflow.com/questions/68881500/how-to-send-an-email-using-python


# background tasks

https://fastapi.tiangolo.com/tutorial/background-tasks/
https://testdriven.io/tips/079fd0c1-3a6c-4dd9-a3fe-807e0c6b0935/
https://stackoverflow.com/questions/67599119/fastapi-asynchronous-background-tasks-blocks-other-requests


# fastapi users
https://fastapi-users.github.io/fastapi-users/

# datepicker
https://getdatepicker.com/6/functions.html

