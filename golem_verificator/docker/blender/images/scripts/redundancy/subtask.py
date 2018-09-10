from ... import compare_images

class Subtask:

    def __init__( self, crop_rect, crop_img ):
        self.crop_rect = crop_rect
        self.crop_img = crop_img

    def find_intersection( self, other ):
        intersection_rect = self.crop_rect.intersect( other.crop_rect )
        