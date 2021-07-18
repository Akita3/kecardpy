
from PIL import Image



class GrayImg:
    
    # Initialization
    def __init__(self, grayImage):
        
        self.width = 0
        self.height = 0
        self.pixels = []
        
        self.setImage( grayImage )
    
    
    
    # set image
    def setImage(self , grayImage ):
        w, h = grayImage.size

        self.width = w
        self.height = h
        self.pixels = [0] * ( self.width * self.height )

        pos = 0
        # Access all pixels.
        for y in range( self.height ):
            for x in range( self.width ):
                # get pixel
                r,g,b = grayImage.getpixel((x,y))
                v1 = r
                self.pixels[ pos ] = v1
                pos += 1
                


    # get pixel
    def getPixel( self , x , y ):
        if x < 0 or self.width <= x: return 0
        if y < 0 or self.height <= y: return 0

        return self.pixels[ y * self.width + x ]


    # set pixel
    def setPixel( self , x , y , value ):
        if x < 0 or self.width <= x: return
        if y < 0 or self.height <= y: return

        self.pixels[ y * self.width + x ] = value


    def getImage(self):
        imgDst = Image.new('RGB', (self.width, self.height))

        # to 2bit grayscale
        pos = 0
        for y in range( self.height ):
            for x in range( self.width ):
                pxl = self.pixels[pos]

                if pxl < 0 : pxl = 0
                if pxl > 255 : pxl = 255

                # set pixel
                imgDst.putpixel((x,y),(pxl,pxl,pxl,0))

                pos += 1

        return imgDst

