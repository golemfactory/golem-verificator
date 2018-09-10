from ... import compare_images

class Subtask:

    def __init__( self, crop_rect, crop_img ):
        self.crop_rect = crop_rect
        self.crop_img = crop_img

    def find_intersection( self, other ):
        intersection_rect = self.crop_rect.intersect( other.crop_rect )

        self_cropped = self.crop_img.crop( intersection_rect - self.crop_rect.topleft() )
        other_cropped = other.crop_img.crop( intersection_rect - other.crop_rect.topleft() )

        return compare_images( self_cropped, other_cropped )