import sys
import time
import machine
import urequests
import json
from machine import I2C
from machine import Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import urllib
from time import sleep
from machine import Pin, PWM
import neopixel


# 16 x 2 LCD I2C Sample Code
# Library from https://github.com/T-622/RPI-PICO-I2C-LCD

# See library GitHub repository for full list of functions and their use

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

print("Running sample code...")

sda = machine.Pin(26)
scl = machine.Pin(27) # NOTE: It is important you change this to match the SDA and SCL pins you are using.
i2c_controller = 1    # Also change this to match the controller you are using (Listed on the Raspberry Pi Pico W Pinout as "I2C0" or "I2C1")
                      # You will need to wire the LCD to your Pi Pico, ensuring that each pin goes to the correct header. The pinout should be written on the LCDs PCB.
                      # You can use either 5V power via VBUS or 3.3V power via either VSYS or 3V(OUT).

i2c = I2C(i2c_controller, sda=sda, scl=scl, freq=400000) 
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

SDA_PIN = 0

SCL_PIN = 1


PLAY_PIN = 2

i2c = I2C(0, sda=machine.Pin(SDA_PIN),

    scl=machine.Pin(SCL_PIN),

    freq=400000)

button_play = Pin(PLAY_PIN, Pin.IN, Pin.PULL_UP)

pwm = PWM(Pin(5))
pwm.freq(50)

pixels = neopixel.Neopixel(29, 0, 16, "GRB")


ssid = 'NA'
password = '12345'


def connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection..')
        time.sleep(3)
    # print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def WeatherCondition(city_weather):
    weather_list = {'Snow': 125 , 'Rain': 65, 'Smoke': 90, 'Haze': 90, 'Fog': 90, 'Clear': 40, 'Mist': 90, 'Clouds': 145, 'Thunderstorm': 65, 'Drizzle': 65}
    dial_position = weather_list[city_weather]
    
    return dial_position

def WeatherDial(angle0, angle1):
    for position in range(angle0, angle1*50, 50):
        pwm.duty_u16(position)
        sleep(0.01)
        
def ResetAll(angle1):
    for position in range(angle1*50, 0, -50):
        pwm.duty_u16(position)
        sleep(0.01)
    lcd.clear()
    time.sleep(1)
    pixels.clear()
    pixels.show()
    
def Lights(city_weather):
    weather_list = {'Snow': (0, 206, 209) , 'Rain': (75, 0, 130), 'Smoke': (200, 200, 200), 'Haze': (200, 200, 200), 'Fog': (200, 200, 200), 'Clear': (100, 65, 0), 'Mist': (200, 200, 200), 'Clouds': (0, 0, 250), 'Thunderstorm': (75, 0, 130), 'Drizzle': (75, 0, 130)}

    for i in range(0, 29):
        pixels.set_pixel(i, weather_list[city_weather])
        pixels.show()
        time.sleep(0.1)

    
        
      
connect ()
api_endpoint = "http://api.openweathermap.org/data/2.5/weather"
apikey = "17d19cc144816e408fb3deab4058568f"

lcd.putstr('Choose a city!')
time.sleep(3)
lcd.clear()

cities = ['Vancouver', 'Victoria', 'Edmonton', 'Calgary', 'Banff', 'Regina', 'Saskatoon', 'Winnipeg', 'Brandon', 'Toronto', 'Ottawa', 'Montreal', 'Halifax', 'Iqaluit']
selected_city = None 
    

while True:
    while button_play.value():
        lcd.putstr('Choose a city!')
        time.sleep(3)
        lcd.clear()
        for i in cities:
            lcd.putstr(i)
            time.sleep(2)
            lcd.clear()
           
            if not button_play.value():
                selected_city = i
                break
            
    if selected_city is not None:
        url = api_endpoint + "?q=" + selected_city + ",CA&appid=" + apikey
        print(url)
        response = urequests.get(url)
        parseResponse = json.loads(response.text)
        temperature = parseResponse['main']['temp']
        weather = parseResponse['weather'][0]['main']
        print(selected_city)
        lcd.move_to(0,0)
        temp = round((temperature-273.15),1)
        string = "City: " + selected_city
        string2 = "Temp: " + str(temp) + " C"
        print(string)
        print(string2)
        lcd.move_to(0,0)
        lcd.putstr(string)
        lcd.move_to(0,1)
        lcd.putstr(string2)
        print(weather)
        dial = WeatherCondition(weather)
        WeatherDial(0, dial)
        Lights(weather)
        time.sleep(4)
        ResetAll(dial)
        
        
     
            
        
        
