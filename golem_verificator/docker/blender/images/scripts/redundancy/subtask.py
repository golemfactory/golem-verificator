from golem_verificator.docker.blender.images.scripts.img_metrics_calculator import default_compare_images

class Rectangle:

    def __init__( self, left, right, top, bottom ):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def intersect( self, other ):
        left = max( self.left, other.left )
        right = min( self.right, other.right )
        top = max( self.top, other.top )
        bottom = min( self.bottom, other.bottom )

        return Rectangle( left, right, top, bottom )

    def topleft( self ):
        return ( self.left, self.top )

    def to_vec( self ):
        return ( self.left, self.top, self.right, self.bottom )

    def __sub__( self, vec ):
        x, y = vec
        return Rectangle( self.left - x, self.right - x, self.top - y, self.bottom - y )

    def __str__(self):
        return "Left = %s, Right = %s, Top = %s, Bottom = %s" % (int(self.left), int(self.right), int(self.top), int(self.bottom))

class Subtask:

    def __init__( self, crop_rect, crop_img ):
        self.crop_rect = crop_rect
        self.crop_img = crop_img

    def find_intersection( self, other ):
        intersection_rect = self.crop_rect.intersect( other.crop_rect )

        self_cropped_rect = intersection_rect - self.crop_rect.topleft()
        self_cropped = self.crop_img.crop( self_cropped_rect.to_vec() )
        other_cropped_rect = intersection_rect - other.crop_rect.topleft()
        other_cropped = other.crop_img.crop( other_cropped_rect.to_vec() )

        result = default_compare_images( self_cropped, other_cropped )
        return result

def find_conflicts( subtasks ):
    conflicts = []

    for subtask1 in subtasks:
        for subtask2 in subtasks:
            if subtask1 != subtask2:
                if subtask1.find_intersection( subtask2 ) == 'FALSE':
                    conflicts.append( (subtask1, subtask2) )

    return conflicts
