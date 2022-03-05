
from PIL import Image
from . import GrayImg


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
    IMG_ASPECT = 1.0 * IMG_WIDTH / IMG_HEIGHT

    # Number of bits and bytes in the image
    IMG_BIT_N = 2
    IMG_BYTE_N = IMG_WIDTH * IMG_HEIGHT * IMG_BIT_N // 8

    # Data packet size
    PACKET_SIZE = 20
    SEND_DATA_SIZE = 240
    # SEND_DATA_SIZE = 16
    
    # Information about the image being sent
    __sendingImage = bytearray( IMG_BYTE_N )
    __sendingNo = 0
    
    
    # Initialization
    def __init__(self):
        pass
    
    
    # 
    def fitImageSize( image ):
        
        width, height = image.size
        
        # 264x176 ? 
        if width == KeImage.IMG_WIDTH and height == KeImage.IMG_HEIGHT:
            return image

        # aspect
        aspect = 1.0 * width / height;

        # reduction
        if aspect > KeImage.IMG_ASPECT :        # width > height
            zoomRatio = 1.0 * KeImage.IMG_HEIGHT / image.height;
            w = int(zoomRatio * width)
            dstImage = image.resize( (w, KeImage.IMG_HEIGHT) , Image.LANCZOS)
            offsetX = (w - KeImage.IMG_WIDTH) // 2;
            dstImage = dstImage.crop( (offsetX , 0 , offsetX + KeImage.IMG_WIDTH , KeImage.IMG_HEIGHT) )
        elif aspect < KeImage.IMG_ASPECT :      # height > width
            zoomRatio = 1.0 * KeImage.IMG_WIDTH / image.width;
            h = int(zoomRatio * height)
            dstImage = image.resize( (KeImage.IMG_WIDTH, h) , Image.LANCZOS)
            offsetY = (h - KeImage.IMG_HEIGHT) // 2
            dstImage = dstImage.crop( (0 , offsetY , KeImage.IMG_WIDTH , offsetY + KeImage.IMG_HEIGHT) )
        elif image.width != KeImage.IMG_WIDTH : # サイズが異なる
            dstImage = image.resize( (KeImage.IMG_WIDTH, KeImage.IMG_HEIGHT) , Image.LANCZOS)

        return dstImage;
    
    

    def colorImageToGray2bitImageNormal( image , th1 = IMG_TH1 , th2 = IMG_TH2 , th3 = IMG_TH3 ):

        # fit image size
        image = KeImage.fitImageSize( image )

        # to grayscale
        gray = image.convert("L").convert("RGB")

        # to 2bit grayscale
        for y in range( KeImage.IMG_HEIGHT ):
            for x in range( KeImage.IMG_WIDTH ):
                # get pixel
                r,g,b = gray.getpixel((x,y))
                
                v1 = r;
                v2 = 0x00
                if v1 < th1: v2 = KeImage.COLOR_0
                elif v1 < th2: v2 = KeImage.COLOR_1
                elif v1 < th3: v2 = KeImage.COLOR_2
                else: v2 = KeImage.COLOR_3

                # setpixel
                gray.putpixel((x,y),(v2,v2,v2,0))

        dstImage = gray;

        return dstImage;


    def colorImageToGray2bitImageDithering( image , th1 = IMG_TH1 , th2 = IMG_TH2 , th3 = IMG_TH3 ):

        # fit image size
        image = KeImage.fitImageSize( image )

        # to grayscale
        gray = image.convert("L").convert("RGB")

        # new GrayImage object
        ditherImg = GrayImg.GrayImg(gray)

        # Calculation for dithering
        for y in range( KeImage.IMG_HEIGHT ):
            for x in range( KeImage.IMG_WIDTH ):
                # get pixel
                pxl = ditherImg.getPixel(x, y)

                if pxl < th1: newpxl = KeImage.COLOR_0
                elif pxl < th2: newpxl = KeImage.COLOR_1
                elif pxl < th3: newpxl = KeImage.COLOR_2
                else :newpxl = KeImage.COLOR_3

                ditherImg.setPixel(x, y, newpxl)
                qerr = pxl - newpxl

                # x+1 , y
                v = ditherImg.getPixel(x+1, y) + 7.0 / 16.0 * qerr
                ditherImg.setPixel(x+1, y , int(v) )

                # x-1 , y+1
                v = ditherImg.getPixel(x-1, y+1) + 3.0 / 16.0 * qerr
                ditherImg.setPixel(x-1, y+1 , int(v) )

                # x , y+1
                v = ditherImg.getPixel(x, y+1) + 5.0 / 16.0 * qerr
                ditherImg.setPixel(x, y+1 , int(v) )

                # x+1 , y+1
                v = ditherImg.getPixel(x+1, y+1) + 1.0 / 16.0 * qerr
                ditherImg.setPixel(x+1, y+1 , int(v) )

        dstImage = ditherImg.getImage();

        return dstImage;


    
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


