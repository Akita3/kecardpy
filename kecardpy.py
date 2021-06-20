
import sys
import asyncio
from lib import KeCardCtrl


IMAGE_FILE_PATH = "sample.png"

async def run():
    
    # initialization
    keCardCtrl = KeCardCtrl.KeCardCtrl()
    
    # Search for devices
    devices = await keCardCtrl.discover();
    if len(devices) == 0:
        print( 'The "(E)CARD" device was not found.' )
        return
    print( 'Discovered Devices.' )
    print( devices )
    
    # Image transfer
    r = await keCardCtrl.transferImage( devices[0].address , IMAGE_FILE_PATH )
    

loop = asyncio.get_event_loop()
loop.run_until_complete(run())

