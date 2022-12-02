from machine import Pin, PWM
fan = PWM(Pin(0))
fan.freq(1000)
fan.duty_u16(30000)
