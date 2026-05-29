import asyncio
from bleak import BleakScanner, BleakClient

CHAR_UUID = "abcd1234-5678-1234-5678-abcdef123456"
TARGET_NAME = "ESP32_Pressure"

import time
import nest_asyncio
nest_asyncio.apply()


def lecture_pression(duree):

    L=[]

    async def main():
        print("Scanning for devices...")
        devices = await BleakScanner.discover()

        for d in devices:

            if d.name and TARGET_NAME in d.name:
                print(d)
                print(f"\nConnecting to {d.name} ({d.address})...")

                async with BleakClient(d.address) as client:
                    print("Connected!")

                    value = await client.read_gatt_char(CHAR_UUID)

                    try:
                        pressure = value.decode("utf-8").strip()
                        print("Pressure:", pressure, "kPa")
                        L.append(pressure)

                    except Exception as e:
                        print("Erreur de décodage:", e)
                        print("Raw bytes:", value)

                break
        else:
            print("Device not found.")

    t=time.time()

    while time.time() - t < duree :
        asyncio.run(main())

    return L