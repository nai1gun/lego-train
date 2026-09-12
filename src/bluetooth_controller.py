#!/usr/bin/env python3
"""
LEGO Train Bluetooth Controller
This script handles Bluetooth connection to LEGO train motors using Bleak library.
"""

import asyncio
import sys
import os

# Проверим, установлены ли необходимые библиотеки
try:
    from bleak import BleakScanner, BleakClient
except ImportError:
    print("Библиотека 'bleak' не установлена. Установите с помощью: pip install bleak")
    sys.exit(1)

# Global variable to store the client for sending commands
client = None

# Port the motor is attached to on the hub, discovered via notifications after connecting
motor_port = None

# LEGO LWP3/LPF2 BLE service UUID, advertised by Powered Up hubs
LEGO_SERVICE_UUID = "00001623-1212-efde-1623-785feabcd123"

# LWP3 characteristic used for both writing commands and receiving notifications
LEGO_CHARACTERISTIC_UUID = "00001624-1212-efde-1623-785feabcd123"

# LWP3 message type: Hub Attached I/O - sent when a motor/sensor connects to a port
MSG_TYPE_HUB_ATTACHED_IO = 0x04
IO_EVENT_ATTACHED = 0x01
IO_EVENT_ATTACHED_VIRTUAL = 0x02

MOTOR_POWER = {"forward": 80, "backward": -80, "stop": 0}

def handle_notification(sender, data):
    """
    Обрабатывает уведомления от хаба, чтобы определить порт, к которому подключён мотор
    """
    global motor_port

    # data: [length, hub_id, message_type, port_id, event, ...]
    if len(data) >= 5 and data[2] == MSG_TYPE_HUB_ATTACHED_IO:
        port_id = data[3]
        event = data[4]
        # External motor/sensor ports are 0 (A) and 1 (B); the hub's own
        # built-in sensors (voltage, current, tilt, etc.) attach on higher
        # port IDs and must be ignored here.
        if event in (IO_EVENT_ATTACHED, IO_EVENT_ATTACHED_VIRTUAL) and port_id <= 1:
            motor_port = port_id
            print(f"Обнаружен мотор на порту {port_id}")

def build_motor_power_command(port_id, power):
    """
    Формирует LWP3-команду "Set Motor Power" для указанного порта
    """
    power_byte = max(-100, min(100, power)) & 0xFF
    payload = bytes([0x00, 0x81, port_id, 0x11, 0x51, 0x00, power_byte])
    return bytes([len(payload) + 1]) + payload

async def find_lego_devices():
    """
    Ищет доступные LEGO устройства в радиусе действия Bluetooth (BLE)
    """
    print("Поиск устройств LEGO...")
    
    try:
        # Сканируем BLE устройства
        devices = await BleakScanner.discover(
            timeout=8,
            return_adv=True
        )
        
        print(f"Найдено {len(devices)} устройств:")
        
        lego_devices = []
        for addr, (device, adv) in devices.items():
            name = adv.local_name or addr
            # LEGO Powered Up hubs advertise the LWP3 service UUID, not a "LEGO"/"Train" name
            if LEGO_SERVICE_UUID in adv.service_uuids:
                print(f"  Найдено LEGO устройство: {name} ({addr})")
                lego_devices.append((device, name))
            else:
                print(f"  Найдено устройство: {name} ({addr})")
        
        return lego_devices
        
    except Exception as e:
        print(f"Ошибка при поиске устройств: {e}")
        return []

async def connect_to_lego_device(ble_device):
    """
    Подключается к указанному LEGO устройству через BLE
    """
    global client

    try:
        print(f"Подключение к устройству {ble_device.address}...")

        # Connect using the BLEDevice object found during scanning, not a bare
        # address string - on Windows, re-resolving by address alone often
        # fails with "Device was not found" once advertising has stopped.
        client = BleakClient(ble_device)

        # Connect to the device
        await client.connect()

        print("Успешно подключено!")

        # Subscribe to notifications and wait briefly for the hub to report
        # which port the motor is attached to (it announces this right after connecting)
        await client.start_notify(LEGO_CHARACTERISTIC_UUID, handle_notification)
        await asyncio.sleep(1)

        if motor_port is None:
            print("Мотор не обнаружен. Проверьте, подключён ли мотор к хабу.")

        return True

    except Exception as e:
        print(f"Ошибка подключения к устройству {ble_device.address}: {e}")
        return False

async def send_command(command):
    """
    Отправляет команду на устройство через BLE
    """
    global client

    try:
        if not (client and client.is_connected):
            print("Нет подключения к устройству")
            return

        if motor_port is None:
            print("Порт мотора неизвестен. Мотор не обнаружен на хабе.")
            return

        power = MOTOR_POWER[command]
        data = build_motor_power_command(motor_port, power)
        await client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, data)
        print(f"Отправлена команда: {command}")
    except Exception as e:
        print(f"Ошибка отправки команды: {e}")

async def main():
    """
    Основная функция для управления LEGO-мотором через Bluetooth (BLE)
    """
    print("=== LEGO Train Bluetooth Controller (using Bleak) ===")
    
    # Поиск устройств
    devices = await find_lego_devices()
    
    if not devices:
        print("LEGO устройства не найдены. Проверьте, включен ли Bluetooth и активно ли устройство.")
        return
    
    # Подключение к первому найденному LEGO-устройству
    ble_device, device_name = devices[0]
    connected = await connect_to_lego_device(ble_device)
    
    if connected:
        try:
            # Примеры команд для управления мотором
            print("Доступные команды:")
            print("  forward - движение вперёд")
            print("  backward - движение назад")
            print("  stop - остановка")
            print("  quit - выход")
            
            while True:
                command = input("Введите команду: ").strip().lower()
                
                if command == "quit":
                    break
                elif command in ["forward", "backward", "stop"]:
                    await send_command(command)
                else:
                    print("Неизвестная команда. Попробуйте снова.")
                    
        except KeyboardInterrupt:
            print("\nПрервано пользователем")
        finally:
            if client and client.is_connected:
                await send_command("stop")
                await client.disconnect()
                print("Соединение закрыто")
    else:
        print("Не удалось подключиться к устройству")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())