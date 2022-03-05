
import asyncio
import time
from bleak import BleakScanner
from bleak import BleakClient
from . import KeImage


class KeCardCtrl:
    
    # Device name of "(E)CARD".
    KE_DEVICE_NAME = 'keCard'
    
    # UUIDs
    KE_UUID_SERVICE_STR = "4ed10001-9710-f67e-885d-dc6be684707b"
    KE_UUID_STATUS_STR = "4ed10002-9710-f67e-885d-dc6be684707b"
    KE_UUID_IMAGE_NO_STR = "4ed10003-9710-f67e-885d-dc6be684707b"
    KE_UUID_COMMAND_STR = "4ed10004-9710-f67e-885d-dc6be684707b"
    
    # Command
    KE_CMD_ERASE_FLASH = 0x01
    KE_CMD_DISPLAY = 0x03

    # Status
    KE_STATUS_RESULT_MASK = 0x0F
    KE_STATUS_RESULT_SUCCESS = 0x01


    # Initialization
    def __init(self):
        pass
    
    
    # This function looks for devises and returns the result as a list
    async def discover(self):
        lst = []
        devices = await BleakScanner.discover()
        for d in devices:
            if d.name == self.KE_DEVICE_NAME:
                lst.append( d )
        return lst
    
    
    # Wait for status completion
    async def waitStatusComplete( self , client , uuidStr ):
        for i in range(5):
            status = await client.read_gatt_char( uuidStr )
            if (status[0] & self.KE_STATUS_RESULT_MASK) == self.KE_STATUS_RESULT_SUCCESS:
                return
            time.sleep(1)
        raise Exception("KE_STATUS did not become complete.")
    
    
    # Image Transfer
    async def transferImage( self , address , imageFileName ):
        
        
        keImage = KeImage.KeImage()
        keImage.setImageFile( imageFileName )
        
        client = BleakClient(address)
        
        try:
            await client.connect()
            
            time.sleep(1)
            
            # Requests the device to erase the flash.
            await client.write_gatt_char( self.KE_UUID_COMMAND_STR , [self.KE_CMD_ERASE_FLASH] )
            print( 'Flash erasing...' )
            
            # Wait until the flash erase is complete.
            await self.waitStatusComplete( client , self.KE_UUID_STATUS_STR );
            print( 'Flash erase completed.' )
            
            
            # Image Transfer
            while keImage.hasFinished() == False:
                data = keImage.getSendPacket()
                await client.write_gatt_char( self.KE_UUID_COMMAND_STR , data )
                time.sleep(0.1)
            print( 'Image transfer completed.' )
            
            
            # Display update request to (E)CARD.
            await client.write_gatt_char( self.KE_UUID_COMMAND_STR , [self.KE_CMD_DISPLAY] )
            print( "Display update request completed." )
            
        except Exception as e:
            client.disconnect()
            print(e)
            return False
        finally:
            pass
        
        return True
    
