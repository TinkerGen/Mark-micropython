from machine import I2C
import time

Mark_i2c_address = 0x58

class MaixS:
    def __init__(self, addr=Mark_i2c_address, drdy=None):
        self.i2c_device = I2C(I2C.I2C0, freq=100000, scl=30, sda=31)
        self._angle_step = 1.8
        self._drive_rpm = 30
        time.sleep(0.1)

    def read(self, reg_base, reg, buf):
        self.write(reg)
        time.sleep(.001)
        self.i2c_device.readfrom_into(59,buf)

    def write(self, buf=None):
        #print(buf)
        if buf is not None:
            self.i2c_device.writeto(Mark_i2c_address, buf)
        # i2c_device.writeto(0x58, bytearray([3,100,100,16,39]))
        # i2c_device.writeto(0x58, bytearray([3,-100,-100,16,39]))

    def servo_angle(self, _servo, _angle):
        if _servo <= 4 and _servo > 0 and _angle <= 180:
            cmd = bytearray([2, _servo-1, _angle])
            self.write(cmd)
            time.sleep(.001)

    def motor_run(self, left_speed, right_speed, time):
        if abs(left_speed) > 100 or abs(right_speed) > 100:
            return
        cmd = bytearray([3, left_speed, right_speed, time & 0xFF, (time >> 8)])
        self.write(cmd)


    def motor_motion(self, speed, dir, time):
        if speed == 0 or speed > 3 or dir > 6 or dir == 0:
            return
        cmd = bytearray([4, speed, dir, time & 0xFF, (time >> 8)])
        self.write(cmd)


    def motor_left(self, left_speed, time):
        if abs(left_speed) > 100:
            return
        cmd = bytearray([6, left_speed, time & 0xFF, (time >> 8)])
        self.write(cmd)


    def motor_right(self, right_speed, time):
        if abs(right_speed) > 100:
            return
        cmd = bytearray([5, right_speed, time & 0xFF, (time >> 8)])
        self.write(cmd)

        self._angle_step = 1.8
        self._drive_rpm = 30

    def drive_set_step(self, step):
        if step == 1.8:
            cmd = bytearray([11, 1])
            self.write(cmd)
        if step == 3.6:
            cmd = bytearray([11, 0])
            self.write(cmd)

    def drive_set_rpm(self, rpm):
        if rpm <= 100 and rpm >= 0:
            cmd = bytearray([12, rpm])
            self.write(cmd)

    def drive_run(self, step):
        cmd = bytearray([9, 1, step & 0xFF, (step >> 8)])
        self.write(cmd)

    def motor_angle(self, Angle, speed, sensitivity):
        if Angle > 90:
            Angle = 90
        if Angle < -90:
            Angle = -90
        init_speed = int(speed*2*(1-sensitivity/100))
        steer = int((Angle/2)*2*(sensitivity/100))
        self.motor_run(init_speed+steer, init_speed-steer, 1000)

Maix_motor = MaixS()
#Maix_motor.drive_set_step(1.8)
#Maix_motor.drive_set_rpm(0)
#Maix_motor.drive_run(200)
