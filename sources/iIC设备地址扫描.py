from machine import Pin, I2C

# 第一组 I2C (比如 OLED + 传感器)
i2c0 = I2C(0, scl=Pin(6), sda=Pin(5), freq=100000)

# 第二组 I2C (比如扩展设备)
i2c1 = I2C(1, scl=Pin(8), sda=Pin(9), freq=100000)

def scan_all():
    dev0 = i2c0.scan()
    dev1 = i2c1.scan()
    print("I2C0 devices:", [hex(d) for d in dev0] if dev0 else "None")
    print("I2C1 devices:", [hex(d) for d in dev1] if dev1 else "None")

# 扫描一次
scan_all()
