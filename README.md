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
(Pin_38 MOSI 1)   Blue
(Pin 2 5v)
(Pin 4 5v)
(Pin 6 GND)
(Pin 9 GND)
```