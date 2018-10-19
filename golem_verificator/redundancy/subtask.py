from golem_verificator.docker.blender.images.scripts.img_metrics_calculator import default_compare_images

class Rectangle:

    def __init__( self, left, right, top, bottom ):
        self.left = int(left)
        self.right = int(right)
        self.top = int(top)
        self.bottom = int(bottom)

    def is_intersect(self, other):
        if self.left >= other.right or self.right <= other.left:
            return False
        if self.top >= other.bottom or self.bottom <= other.top:
            return False
        return True

    def intersect( self, other ):
        if not self.is_intersect(other):
            return None
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
        if not intersection_rect:
            return None

        return intersection_rect 

    def __str__(self):
        return "Subtask %s" % (self.crop_rect.__str__())

def converet_to_subtasks_coords(subtask, redundandt, intersection):
    subtask_cropped_rect = intersection - subtask.crop_rect.topleft()
    subtask_cropped = subtask.crop_img.crop( subtask_cropped_rect.to_vec() )
    redundandt_cropped_rect = intersection - redundandt.crop_rect.topleft()
    redundandt_cropped = redundandt.crop_img.crop( redundandt_cropped_rect.to_vec() )

    return subtask_cropped, redundandt_cropped

def verify_intersection(subtask_cropped, redundandt_cropped):
    if subtask_cropped.size != redundandt_cropped.size or \
    too_small_for_compare( subtask_cropped ) or too_small_for_compare( redundandt_cropped ):
        print("To small area to calculate metrics, ignroing")
        return 'TRUE'
    return default_compare_images( subtask_cropped, redundandt_cropped )

def too_small_for_compare( image ):
    width, height = image.size
    if width < 8 or height < 8:
        return True
    else:
        return False

def find_conflicts( subtasks, redundancy_subtasks ):
    conflicts = []

    for subtask1 in subtasks:
        for subtask2 in redundancy_subtasks:
            if subtask1 != subtask2:
                intersection = subtask1.find_intersection( subtask2 )
                if intersection:
                    subtask_cropped, redundandt_cropped = converet_to_subtasks_coords(
                        subtask1, subtask2, intersection)
                    result = verify_intersection(
                        subtask_cropped, redundandt_cropped)
                if result == 'FALSE':
                   conflicts.append( (subtask1, subtask2, intersection) )

    return conflicts
