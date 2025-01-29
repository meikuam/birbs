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

i2c access

```
# create file /etc/udev/rules.d/50-i2c.rules
# with content

SUBSYSTEM=="i2c-dev", GROUP="i2c", MODE="0660"

# next
sudo groupadd i2c
sudo adduser "$USER" i2c

```

gpio access

```
# create /etc/udev/rules.d/50-gpio.rules

SUBSYSTEM=="gpio",GROUP="gpio", MODE="0660"

sudo groupadd gpio
sudo adduser "$USER" gpio
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

sudo apt install arduino-ctags

# fix error workaround (orpi3lts)
cd .arduino15/packages/builtin/tools/ctags/5.8-arduino11
mv ctags orig.ctags
ln -s /usr/bin/arduino-ctags ctags

arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli lib install IRremote
arduino-cli lib install NewPing
arduino-cli lib install Servo
arduino-cli lib install PCA9685_RT
arduino-cli lib install iarduino_i2c_connect
arduino-cli lib install iarduino_HC_SR04_tmr

arduino-cli config init
arduino-cli config set library.enable_unsafe_install true

#arduino-cli lib install --git-url https://github.com/tremaru/iarduino_I2C_connect.git

arduino-cli lib install --git-url https://github.com/meikuam/iarduino_I2C_connect.git


# nano
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328old arduino_controller
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:nano:cpu=atmega328old arduino_controller

# mega
arduino-cli compile --fqbn arduino:avr:mega:cpu=atmega2560 arduino_controller
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:mega:cpu=atmega2560 arduino_controller
```

## 7. setup variables

```

```

## 8. docker-compose up

```
./docker/run_prod.sh
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
  + фоновый процесс который по расписанию работает
  + логгирование информации через телеграм бота
  + крутую ui для настройки всяких штук (ага щас)


- серводвигатели штука
  https://github.com/RobTillaart/PCA9685_RT

- еще надо разобраться с уровнем воды




https://lesson.iarduino.ru/page/urok-26-3-soedinyaem-dve-arduino-po-shine-i2c/

https://www.instructables.com/Arduino-I2C-and-Multiple-Slaves/



https://github.com/tremaru/iarduino_I2C_connect/tree/master
https://lesson.iarduino.ru/page/urok-26-3-soedinyaem-dve-arduino-po-shine-i2c/

## add to fstab sd card:

/etc/fstab

```
UUID=%your uuid%     /media/data   ext4    rw,suid,auto,user,exec,nofail   0    0
```

## move docker root to sd card:

https://www.ibm.com/docs/en/z-logdata-analytics/5.1.0?topic=software-relocating-docker-root-directory

```
sudo systemctl stop docker.socket
sudo systemctl stop containerd
sudo mkdir -p /media/data
sudo mv /var/lib/docker /media/data

sudo vim /etc/docker/daemon.json

{
  "data-root": "/media/data/docker"
}

sudo systemctl start docker

docker info -f '{{ .DockerRootDir}}'
```


https://python-periphery.readthedocs.io/en/latest/_modules/periphery/i2c.html#I2C
https://micro-pi.ru/%D1%81%D0%B5%D1%80%D0%B2%D0%BE-sg90-pca9685-python-raspberry-pi/
https://github.com/adafruit/Adafruit_Python_PCA9685
https://github.com/adafruit/Adafruit_CircuitPython_PCA9685/tree/main



sudo apt install i2c-tools