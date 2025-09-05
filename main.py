print("Project: Smart Water Quality Monitoring & Wastewater Management System")
print("This program will monitor water quality (pH and TDS simulated) and detect tank/bin fill level using an ultrasonic sensor.")
print("Trigger alerts on an OLED screen and with a buzzer if values go beyond thresholds.")
print("Date: 1/05/2025")

# Import library / module
from machine import Pin, PWM, SoftI2C, ADC
import ultrasonic_library
import oled_library
from time import sleep

# Pin Declaration
TRIG = Pin(13, Pin.IN)
ECHO = Pin(12, Pin.IN)
red_pin = Pin(14, Pin.OUT)
blue_pin = Pin(25, Pin.OUT)
green_pin = Pin(27, Pin.OUT)
buzzer = PWM(Pin(18, Pin.OUT))
SCL1_Pin = Pin(23)
SDA1_Pin = Pin(22)
OLED1_Pin = SoftI2C(scl=SCL1_Pin, sda=SDA1_Pin)

# **Uncommented OLED2 Pin declaration**
SCL2_Pin = Pin(5)
SDA2_Pin = Pin(19)
OLED2_Pin = SoftI2C(scl=SCL2_Pin, sda=SDA2_Pin)

def set_rgb(r, g, b):
    red_pin.value(r)
    green_pin.value(g)
    blue_pin.value(b)

# Potentiometers as pH and TDS sensors
ph_sensor = ADC(Pin(34))
tds_sensor = ADC(Pin(35))
ph_sensor.atten(ADC.ATTN_11DB)
tds_sensor.atten(ADC.ATTN_11DB)

# Object Declaration
water_level_sensor = ultrasonic_library.HCSR04(trigger_pin=TRIG, echo_pin=ECHO, echo_timeout_us=500*2*30)
screen1 = oled_library.SSD1306_I2C(width=128, height=64, i2c=OLED1_Pin)

# **Uncommented screen2 initialization**
screen2 = oled_library.SSD1306_I2C(width=128, height=64, i2c=OLED2_Pin)

# Main Program Loop
while True:
    measure_distance = water_level_sensor.distance_cm()
    ph = ph_sensor.read() / 4095 * 14
    tds = tds_sensor.read() / 4095 * 1000

    print("Water level:", measure_distance, "cm")
    print("pH:", round(ph, 1), " | TDS:", int(tds), "ppm")

    # OLED Display Output
    # Display 1
    screen1.fill(0)
    screen1.text("Water level:", 5, 10)
    screen1.text(str(measure_distance) + " cm", 5, 30)

    # Water level alerts
    if measure_distance >= 400:
        set_rgb(1, 0, 0)  # Red
        status = "CRITICAL LEVEL !"
        buzzer.init(freq=1000, duty=70)
        sleep(0.1)

    elif 300 < measure_distance < 400:
        set_rgb(1, 1, 0)  # Orange (Red + Green)
        status = "WARNING LEVEL!"
        buzzer.init(freq=1000, duty=70)
        sleep(0.1)
        buzzer.duty(0)
        sleep(0.25)

    else:
        set_rgb(0, 1, 0)  # Green
        status = "SAFE LEVEL"
        buzzer.duty(0)

    screen1.text(status, 5, 52)
    screen1.show()

    # Display 2
    screen2.fill(0)
    screen2.text("pH: {:.1f}".format(ph), 5, 10)
    screen2.text("TDS: {} ppm".format(int(tds)), 5, 20)

    # Water quality alerts
    if ph < 6.5 or ph > 8.5 or tds > 500:
        set_rgb(0, 0, 1)  # Blue
        status = "WATER UNSAFE !"
        buzzer.init(freq=1000, duty=70)
        sleep(0.25)

    else:
        set_rgb(0, 0, 0)  # LED off
        status = "WATER SAFE"
        buzzer.duty(0)

    screen2.text(status, 5, 52)
    screen2.show()

    # System delay
    sleep(0.5)