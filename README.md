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