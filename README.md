# AlarmClockPi





```bash
sudo apt install apt-file vim xrdp glances swig liblgpio-dev python3-lgpio
```

To build venv  (do from within the main folder)
```bash
python3 -m venv venv
source venv/bin/activate
pip list
pip cache purge
pip install -r ~/work/AlarmClockPi/requirements.txt

```

# Create alarmuser

```bash
sudo useradd -r -s /bin/false alarmuser
sudo usermod -aG gpio alarmuser
sudo usermod -aG i2c alarmuser
sudo usermod -aG spi alarmuser
```

# Setup Raspberry pi options

```bash
sudo raspi-config
```

## Enable spi 1

Edit `/boot/firmware/config.txt` and add the following
```bash
# enable spi1
dtoverlay=spi1-3cs
```



```bash
# enable spi and i2c
sudo reboot now
```

# fix permissions for service

```bash
mkdir -p ~/work
git clone git@github.com:Jester3141/AlarmClockPi.git
chmod a+rx /home/mtomer
chmod a+w /home/mtomer/work/AlarmClockPi
```


# Install as systemd service

```bash
sudo cp alarmclock.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now alarmclock.service
```


## Pinout for LCD

```
(Pin_23 SCLK)   Grey          (21)         EMPTY            (19 MOSI) Purple                (17 3.3v)  White
(Pin_24 GPIO_8) Green         (22 GPIO_25) Brown            (20 GND)  Black                 (18 GPIO_24) Blue
```


## Pinout for LED

```
(Pin_38 MOSI 1)   Blue   ......   (Pin 14 GND) Grey       (Pin 6 GND) Black       (Pin 4 5v) White        (Pin 2 5v) White
```


## Pinout for LUX Sensor

```
(Pin 9 GND) Brown       (Pin 5 SCL) Orange       (Pin 3 SDA) Yellow        (Pin 1 3.3v) Red
```


## Pinout for Button

S / VIn unconnected
```
(Pin 33 GPIO 13) brown -----> + or OUT
(Pin 34 GND) Black -----> - or GND
```




## pip freeze

Adafruit-Blinka==9.2.0
Adafruit-Blinka-Raspberry-Pi5-Neopixel==1.0.0rc2
adafruit-circuitpython-busdevice==5.2.17
adafruit-circuitpython-connectionmanager==3.1.8
adafruit-circuitpython-neopixel==6.4.2
adafruit-circuitpython-neopixel-spi==1.0.16
adafruit-circuitpython-pixelbuf==2.1.0
adafruit-circuitpython-requests==4.1.17
adafruit-circuitpython-typing==1.12.3
Adafruit-PlatformDetect==3.89.1
Adafruit_PureIO==1.1.12
binho-host-adapter==0.1.6
cbor2==6.1.5
colormath2==3.0.3
lgpio==0.2.2.0
luma.core==2.6.0
luma.oled==3.16.0
networkx==3.7
numpy==2.5.4
pillow==12.3.0
pyftdi==0.57.2
pyserial==3.5
pyusb==1.3.1
rpi-lgpio==0.6
RPi.GPIO==0.7.1
rpi_ws281x==5.0.0
smbus2==0.6.1
spectra==0.1.0
spidev==3.8
sysv_ipc==1.2.0
typing_extensions==4.16.0