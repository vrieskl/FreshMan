# Freshman

Software for air quality @home

## PicoAirQuality
Airqualitiy is measured with a SGP40 from DFROBOT.
Clock on pin 7, data on pin 6.
The software has two parts, one part on the pico, the other on a server (e.g. Raspberry Pi zero to four).
The Pico sends data to a MQTT queue.

Copy to the Raspberry Pico W:
- pico/secrets.py (adapt to your situation)
- pico/PicoAirQuality.py as main.py (adapt line 10-12 for your MQTT configuration)
- pico/lib/umqtt/simple.py
- pico/lib/sgp40.py

On a server:
- server/classes/VOC_Algorithm.py
- server/PicoAirQuality.py
- server/config2.json (adapt to your MQTT configuration)
