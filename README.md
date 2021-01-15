Micropython + LVGL firmware for ESP32 PSRAM and 16MB flash boards added

# SmartHome-Central

My personal project to learn [Micropython](https://github.com/micropython/micropython) and by utilizing [LVGL](https://github.com/lvgl/lv_binding_micropython) on ILI9341 display

![How it looks](https://user-images.githubusercontent.com/2889604/102701277-187aeb80-425e-11eb-94d0-472f06900519.jpg)

Wire connection diagram

| ESP32 Pin | ILI9341 PIN |
|-----|-----|
| 3v3 | VCC |
| GND | GND |
| 26 | CS |
| 33 | Reset |
| 27 | DC |
| 23 | SDI (Mosi) |
| 18 | SCK |
| 32 | LED |
| 19 | SDO (Miso) |
| 14 | T_CLK |
| 15 | T_CS |
| 13 | T_DIN |
| 12 | T_DO |
| 35 (not used) | T_IRQ |



I could not do with just one ESP32 device (and avoid proxy and MQTT) I could not achieve BLE + HTTP + LVGL in one ESP32 generic device (no PSRAM chip). LVGL [does not play nice](https://github.com/lvgl/lv_binding_micropython/issues/109) together with BLE so I came up with idea to split into two devices- [Proxy](https://github.com/lixas/SmartHome-Central) and Central.

As main thermometers, capable of advertising data via BLE I've used cheap (4€) Xiaomi Thermometer [LYWSD03MMC](https://www.aliexpress.com/item/4000427410383.html)  with [custom firmware](https://github.com/atc1441/ATC_MiThermometer)

![Solution Diagram](https://user-images.githubusercontent.com/2889604/102700761-19f5e500-4259-11eb-84ff-5db9f9a1eae0.jpeg)

It uses OpenWeatherMap as weather data provider. To use your location, edit `sensor/weather.py` @115 request url



Planned:
* OTA (Over-The-Air) updates
* Shopping list
