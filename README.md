# birbs


# howto start

## 1. download OS for orangepi 3 lts

[ubuntu](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-pi-3-LTS.html) (preference)

[armbian](https://www.armbian.com/orangepi3-lts)

## 2. install on emmc

https://jumptuck.com/blog/2023-02-13-install-linux-orange-pi-3-lts-emmc/

```
nand-sata-install
```

## 3. setup wifi

```
sudo nmcli dev wifi connect %yourwifissid% password '%yourwifipass%'

nmcli connection modify %yourwifissid% connection.autoconnect yes
nmcli device set wlan0 autoconnect yes
```

## 4. setup dtb overlays for spi

in `/boot/orangepiEnv.txt`

```
overlays=spi-spidev1
param_spidev_spi_bus=1
param_spidev_spi_cs=0
param_spidev_max_freq=100000000
```

examples with dtc and fdtdump/fdtput (to modify something):
```
sudo apt install device-tree-compiler
sudo fdtput sun50i-h6-orangepi-3-lts.dtb /soc/spi@5011000 status -t s "okay"
sudo fdtdump sun50i-h6-orangepi-3-lts.dtb
dtc -I dtb -O dts sun50i-h6-orangepi-3-lts.dtb
```


[spi access](https://forum.up-community.org/discussion/2141/solved-tutorial-gpio-i2c-spi-access-without-root-permissions)

```
# create file: /etc/udev/rules.d/50-spi.rules
# with content:

SUBSYSTEM=="spidev", GROUP="spiuser", MODE="0660"

# next:
sudo groupadd spiuser
sudo adduser "$USER" spiuser
```



## 5. install docker

```
sudo apt install ca-certificates curl gnupg lsb-release
# gpg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
# repo
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# install
sudo apt update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

## 6. install arduino-cli & compile code
```
mkdir ~/arduino-cli/bin
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/arduino-cli/bin sh
echo 'export PATH="${HOME}/arduino-cli/bin:${PATH}"' >> ~/.bashrc

arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli lib install IRremote
arduino-cli lib install NewPing
arduino-cli lib install Servo

# nano
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328old arduino_controller
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:nano:cpu=atmega328old arduino_controller

# mega
arduino-cli compile --fqbn arduino:avr:mega:cpu=atmega2560 arduino_controller
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:mega:cpu=atmega2560 arduino_controller
```

### ssh forwating

```
ssh -L 127.0.0.1:5000:localhost:5000 orangepi@31.211.117.161 -p 9622
```



# additional

```
sudo apt-get install libpq-dev
sudo apt-get install python3-psycopg2
```

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

http://arduino.zl3p.com/infa/pins_nano





https://github.com/vsergeev/python-periphery
https://gist.github.com/chrismeyersfsu/3317769
https://forum.arduino.cc/t/spi-slave-mode-example-code/66617

https://github.com/orangepi-xunlong/wiringOP
https://micro-pi.ru/%D0%B2%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%88%D0%B8%D0%BD%D1%8B-spi-%D0%BD%D0%B0-orange-pi/#_SPI__414_Ubuntu_1804





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


