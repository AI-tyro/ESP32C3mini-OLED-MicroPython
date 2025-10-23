# 接线说明,SDA=GPIO5,SCL=GPIO6
from machine import Pin, I2C
import time
import ssd1306
from aht0_bmp280 import BMP280,AHT20 
# 这里用改过的 AHT20 类（实际是 AHT10 协议）类名未改

# ======================
# OLED 初始化
# ======================
i2c = I2C(0, scl=Pin(6), sda=Pin(5), freq=100000)  # 屏幕和传感器共用 I2C
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


def show_text(msg):
    """
    自动分行显示字符串
    - 每行最多 9 个字符
    - 最多显示 4 行
    - 起始偏移量 x=27, y=24
    """
    oled.fill(0)
    lines = []
    for i in range(0, len(msg), 9):
        lines.append(msg[i:i+9])
        if len(lines) >= 4:
            break
    y = 24
    for line in lines:
        oled.text(line, 27, y)
        y += 10
    oled.show()

# ======================
# 传感器初始化
# ======================
aht = AHT20(i2c, address=0x38)
bmp = BMP280(i2c, address=0x77)

# ======================
# 主循环
# ======================
while True:
    try:
        # AHT10 (丝印AHT20) 读温湿度
        hum, t_aht = aht.read()
        # BMP280 读温度和气压
        t_bmp = bmp.read_temperature()
        press = bmp.read_pressure()

        print(f"AHT -> Temp: {t_aht:.2f} °C  Hum: {hum:.2f} %")
        print(f"BMP -> Temp: {t_bmp:.2f} °C  Press: {press:.2f} hPa")

        # OLED 显示
        # 四行内容：AHT温度、AHT湿度、BMP温度、BMP气压
        show_text(
            f"A T:{t_aht:.1f}C"
            f"  H:{hum:.1f}%"
            f"B T:{t_bmp:.1f}C"
            f"P:{press:.0f}hPa"
        )
    except Exception as e:
        print("Error:", e)
        show_text("Sensor Err")

    time.sleep(2)

