import network
import machine
import time
import ssd1306
import ubluetooth

# ======================
# OLED 初始化
# ======================
i2c = machine.SoftI2C(scl=machine.Pin(6), sda=machine.Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def show_text(msg):
    """
    自动分行显示字符串
    - 每行最多 9 个字符
    - 最多显示 4 行
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
# WiFi AP 模式
# ======================
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32WiFi", password="12345678")

# ======================
# BLE 初始化
# ======================
class BLEPeripheral:
    def __init__(self, name="ESP32BLE"):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)
        self.ble.irq(self.bt_irq)
        self.connected = False
        self.register()
        self.advertiser()

    def bt_irq(self, event, data):
        if event == 1:  # central connected
            self.connected = True
        elif event == 2:  # central disconnected
            self.connected = False
            self.advertiser()

    def register(self):
        UART_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
        UART_TX   = (ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
                     ubluetooth.FLAG_NOTIFY,)
        UART_RX   = (ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
                     ubluetooth.FLAG_WRITE,)
        UART_SERVICE = (UART_UUID, (UART_TX, UART_RX,))
        SERVICES = (UART_SERVICE,)
        ((self.tx, self.rx,),) = self.ble.gatts_register_services(SERVICES)

    def advertiser(self):
        name = bytes("ESP32BLE", "utf-8")
        adv_data = bytearray(b"\x02\x01\x06") + bytearray((len(name)+1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)

# 启动 BLE
ble = BLEPeripheral("ESP32BLE")

# ======================
# 主逻辑
# ======================
show_text("ESP32 Ready")

wifi_locked = False
ble_locked = False
start_time = time.time()

while True:
    # 如果 WiFi 已连接，锁定 WiFi，关闭 BLE
    if ap.isconnected() and not wifi_locked and not ble_locked:
        wifi_locked = True
        ble_locked = False
        ble.ble.active(False)   # 关闭 BLE
        ip = ap.ifconfig()[0]
        show_text("WiFi Conn" + "IP:" + ip)

    # 如果 BLE 已连接，锁定 BLE，关闭 WiFi
    if ble.connected and not wifi_locked and not ble_locked:
        ble_locked = True
        wifi_locked = False
        ap.active(False)        # 关闭 WiFi
        show_text("BLE Conn")

    # 如果都没连，显示等待
    if not wifi_locked and not ble_locked:
        elapsed = time.time() - start_time
        if elapsed > 60:  # 超过 60 秒无人连接 → 节能
            ap.active(False)
            ble.ble.active(False)
            show_text("Power Save")
            break
        else:
            show_text("ESP32 Ready" + "Waiting...")

    time.sleep(1)
