import pywt
import numpy
from PIL import Image

import sys

def calculate_sum( coeff ):
    return sum( sum( coeff ** 2 ) )

def calculate_size( coeff ):
    shape = coeff.shape
    return shape[ 0 ] * shape[ 1 ]

def calculate_mse( coeff1, coeff2, low, high ):
    if low == high:
        if low == 0:
            high = low + 1
        else:
            low = high - 1
    suma = 0
    num = 0
    for i in range( low, high ):
        if type( coeff1[ i ] ) is tuple:
            suma += calculate_sum( coeff1[ i ][ 0 ] - coeff2[ i ][ 0 ] )
            suma += calculate_sum( coeff1[ i ][ 1 ] - coeff2[ i ][ 1 ] )
            suma += calculate_sum( coeff1[ i ][ 2 ] - coeff2[ i ][ 2 ] )
        else:
            suma += calculate_sum(coeff1[i] - coeff2[i] )
        num += len( coeff1[ i ] )
    if( num == 0 ):
        return 0
    else:
        return suma / num

## ======================= ##
##
class MetricWavelet:

    ## ======================= ##
    ##
    @staticmethod
    def compute_metrics( image1, image2):

        image1 = image1.convert("RGB")
        image2 = image2.convert("RGB")

        np_image1 = numpy.array(image1)
        np_image2 = numpy.array(image2)

        result = dict()
        result["wavelet_low"] = 0
        result["wavelet_mid"] = 0
        result["wavelet_high"] = 0

        for i in range(0,3):
            coeff1 = pywt.wavedec2( np_image1[...,i], "db4" )
            coeff2 = pywt.wavedec2( np_image2[...,i], "db4" )

            len_div_3 = int( len( coeff1 ) / 3 )
            len_two_thirds = int( len( coeff1 ) * 2 / 3 )
            len_total = len( coeff1 )

            result[ "wavelet_low" ] = result[ "wavelet_low" ] + calculate_mse( coeff1, coeff2, 0, len_div_3 )
            result[ "wavelet_mid" ] = result[ "wavelet_mid" ] + calculate_mse( coeff1, coeff2, len_div_3, len_two_thirds )
            result[ "wavelet_high" ] = result[ "wavelet_high" ] + calculate_mse( coeff1, coeff2, len_two_thirds, len_total )

        return result

    ## ======================= ##
    ##
    @staticmethod
    def get_labels():
        return [ "wavelet_low", "wavelet_mid", "wavelet_high" ]


## ======================= ##
##
def run():
    first_img = Image.open( sys.argv[1] )
    second_img = Image.open( sys.argv[2] )

    ssim = MetricWavelet()

    print(ssim.compute_metrics(first_img, second_img))


if __name__ == "__main__":
    run()
