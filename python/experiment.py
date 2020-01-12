import time

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

SERVO_CONTROL_PIN = 13


GPIO.setup(SERVO_CONTROL_PIN, GPIO.OUT)

pwm=GPIO.PWM(SERVO_CONTROL_PIN, 50)

pwm.start(0)

def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_CONTROL_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO_CONTROL_PIN, False)
    pwm.ChangeDutyCycle(0)


SetAngle(90)

SetAngle(15)

SetAngle(30)

pwm.stop()
GPIO.cleanup()