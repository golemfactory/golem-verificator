import os
from PIL import Image
from partitioning import get_subtasks_coord
from partitioning import get_redundancy_segment_random
from partitioning import get_redundancy_coord
from partitioning import Context, get_subtasks_size
from subtask import Subtask
from subtask import find_conflicts
from golem_verificator.docker.blender.images.scripts import img_metrics_calculator

img_metrics_calculator.TREE_PATH = os.path.normpath("golem_verificator/docker/blender/images/scripts/tree35_[crr=87.71][frr=0.92].pkl") 
test_path = os.path.normpath('/home/elfoniok/golem-verificator/golem_verificator/docker/blender/images/scripts/redundancy/barcelona_[samples=8725].png')

def subtasks_generator(task, subtasks_number):
    subtasks_coords = get_subtasks_coord(task, subtasks_number)
    crops = []
    counter = 0
    for rect in subtasks_coords:
        crop = task.crop((rect.left, rect.top, rect.right, rect.bottom))
        p_map = crop.load()
        for i in range(crop.size[0]):    # for every col:
            for j in range(crop.size[1]):    # For every row
                p_map[i,j] = (i, j, 100) # set the colour accordingly
        crops.append(crop)
        counter += 1
        crop.save("Subtask " + str(counter) + ".png")
    return crops, subtasks_coords

def redundancy_generator(task, K, context, algorithm):
    coords = get_redundancy_coord(task, K, context, algorithm)
    crops = []
    counter = 0
    for rect in coords:
        crop = task.crop((rect.left, rect.top, rect.right, rect.bottom))
        crops.append(crop)
        counter += 1
        crop.save("Redundancy " + str(counter) + ".png")
    return crops, coords

def make_subtasks(images, coords):
    subtasks = []
    for img, coords in zip( images, coords):
        subtasks.append(Subtask(coords, img))
    return subtasks

if __name__ == '__main__':
    task = Image.open(test_path)
    subtasks_count = 12
    K = 1.5
    subtask_size = get_subtasks_size(task.height, subtasks_count)
    context = Context(task.width, subtask_size)
    subtasks, s_coords = subtasks_generator(task, subtasks_count)
    #for s in s_coords:
    #   print(s)
    input1 = make_subtasks(subtasks, s_coords)
    redundancies, r_coords = redundancy_generator(task, K, context, get_redundancy_segment_random)
    input2 = make_subtasks(redundancies, r_coords)
    conflicts = find_conflicts(input1, input2)
    
    conflicts_map = Image.new('RGB', (800,600), "white")
    pixels = conflicts_map.load()
    
    counter = 0
    for c in conflicts:
        #print(str(c[0]) + " " + str(c[1] )
        print(str(c[2]))
        
        if counter % 3 == 0:
            color = ( 0, 255, 0 )
        elif counter % 3 == 1:
            color = ( 0, 0, 255 )
        elif counter % 3 == 2:
            color = ( 255, 0, 0 )

        counter +=1
        for i in range(int(c[2].left), int(c[2].right)):    # for every col:
            for j in range(int(c[2].top), int(c[2].bottom)):    # For every row
               pixels[i,j] = color
    
    conflicts_map.save("map.png")
