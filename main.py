import asyncio
from bleak import BleakScanner,BleakClient,exc
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice

TEMP_HUM_WRITE_HANDLE = 0x0038
TEMP_HUM_READ_HANDLE = "363c4b"
TEMP_HUM_WRITE_VALUE = bytearray([0x01, 0x00])

UUID_TEMP_SERVICE = "ebe0ccb0-7a0a-4b0c-8a1a-6ff2997da3a6"
UUID_TEMP_CHARACT = "ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6"


async def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """Simple notification handler which prints the data received."""
    #print(characteristic.properties,characteristic.service_uuid,characteristic.uuid)
    print(mac,characteristic.description, (data[0] | (data[1] << 8)) * 0.01 ,"C", data[2]*1, "%", data[3] | (data[4] << 8),"mV" )
    stop_event.set()


async def connect(device):
    async with BleakClient(device) as client:
        try:
            for serv in client.services:
                if serv.uuid == UUID_TEMP_SERVICE:
                    tempService = serv
                    for char in tempService.characteristics:
                        if char.uuid == UUID_TEMP_CHARACT:
                            #print("Subbing")
                            # get notification from sensor
                            global stop_event
                            stop_event = asyncio.Event()
                            global mac
                            mac = client.address
                            await client.start_notify(char,notification_handler)
                            #await asyncio.sleep(12.0)
                            await stop_event.wait()
                            #print("finished")
                            await client.stop_notify(char)
        except:
            print("boom2")
        finally:
            print("Disconnect")
            await client.disconnect()

async def main():
    scannedList = []
    while True:
        devices:list[BLEDevice] = await BleakScanner.discover(timeout=15)
        for d in devices:
            dev:BLEDevice = d
            print(d)
        for d in devices:
            dev:BLEDevice = d
            n:str = dev.name
            if(n is not None):
                if("LYW" in n ):
                    if(d.address not in scannedList):
                        print(dev,"->Found")
                        await connect(d)
                        scannedList.append(d.address)
        
        await asyncio.sleep(1.0)
        print("scanning again")
        
asyncio.run(main())