# AlarmClockPi

```bash
sudo apt install swig liblgpio-dev python3-lgpio
```

To build venv
```bash
python3 -m venv venv2
source venv2/bin/activate
pip list
pip cache purge
pip install -r ~/work/AlarmClockPi/requirements.txt

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