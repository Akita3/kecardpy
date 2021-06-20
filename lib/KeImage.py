
from PIL import Image


class KeImage:
    
    # Four grayscale values
    COLOR_0 = 0
    COLOR_1 = 127
    COLOR_2 = 195
    COLOR_3 = 255
    
    # Threshold to convert from 256 steps to 4 steps
    IMG_TH1 = 64
    IMG_TH2 = 160
    IMG_TH3 = 224

    # Image width, height, and aspect ratio
    IMG_WIDTH = 264
    IMG_HEIGHT = 176
    IMG_ASPECT = IMG_WIDTH / IMG_HEIGHT

    # Number of bits and bytes in the image
    IMG_BIT_N = 2
    IMG_BYTE_N = IMG_WIDTH * IMG_HEIGHT * IMG_BIT_N // 8

    # Data packet size
    PACKET_SIZE = 20
    SEND_DATA_SIZE = 128
    
    # Information about the image being sent
    __sendingImage = bytearray( IMG_BYTE_N )
    __sendingNo = 0
    
    
    # Initialization
    def __init(self):
        pass
    
    
    # Get the maximum value of the sending number.
    def getSendNoMax(self):
        
        if len( self.__sendingImage ) == 0:
            return 0
        
        n = len( self.__sendingImage ) // self.SEND_DATA_SIZE
        if len( self.__sendingImage ) % self.SEND_DATA_SIZE != 0: n += 1

        return n;

    
    # Load an image file
    def __loadImageFile( self , fileName ):
        
        im = Image.open( fileName )
        size = im.size

        if self.IMG_WIDTH != size[0] or self.IMG_HEIGHT != size[1]:
            im = im.resize((self.IMG_WIDTH, self.IMG_HEIGHT), Image.LANCZOS)

        im = im.convert('RGB')
        
        return im

    
    # Convert color images to 2-bit grayscale
    def __colorImageToGray2bit( self , image ):
        
        byteArray = bytearray( self.IMG_BYTE_N )
        pxlNo = 0
        
        # Rotate it 90 degrees to the left.
        for x in reversed(range(image.size[0])):
            for y in range(image.size[1]):
                r,g,b = image.getpixel((x,y))
                pxl = (r + g + b) / 3
                
                vl = 0
                if pxl >= self.IMG_TH3: vl = 3
                elif pxl >= self.IMG_TH2: vl = 2
                elif pxl >= self.IMG_TH1: vl = 1
                
                arrayNo = pxlNo // (8 // self.IMG_BIT_N)
                shift = ( 3 - pxlNo % (8 // self.IMG_BIT_N) ) * self.IMG_BIT_N
                
                bit = vl << shift
                byteArray[arrayNo] |= bit
                
                pxlNo += 1
        
        return byteArray
        
    
    # Set the image file
    def setImageFile( self , fileName ):
        
        im = self.__loadImageFile( fileName )
        self.__sendingImage = self.__colorImageToGray2bit( im )
        self.__sendingNo = 0
        
        return True
    
    
    # Get packets to send
    def getSendPacket( self ):
        
        if self.hasFinished(): return null
        
        header = bytearray( 2 )
        header[0] = self.__sendingNo & 0xFF
        header[1] = (self.__sendingNo >> 8) & 0xFF
        
        pos = self.__sendingNo * self.SEND_DATA_SIZE
        size = self.IMG_BYTE_N - pos
        if size > self.SEND_DATA_SIZE: size = self.SEND_DATA_SIZE
        data = self.__sendingImage[ pos : pos + size ]
        
        pkt = header + data
        
        self.__sendingNo += 1
        
        return pkt
    
    
    # Get progress
    def getProgress( self ):
        v = self.__sendingNo * 100 // self.getSendNoMax()
        return v


    # Is it done?
    def hasFinished( self ):
        if self.getSendNoMax() <= self.__sendingNo:
            return True
        return False

    # Reset progress
    def resetProgress( self ):
        self.__sendingNo = 0


