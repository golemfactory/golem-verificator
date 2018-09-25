import os
from PIL import Image
from partitioning import get_subtasks_coord
from partitioning import get_redundancy_segment_random
from partitioning import get_redundancy_coord
from partitioning import Context, get_subtasks_size
from subtask import Subtask
from subtask import find_conflicts

test_path = os.path.normpath('/home/elfoniok/golem-verificator/golem_verificator/docker/blender/images/scripts/redundancy/barcelona_[samples=8725].png')

def subtasks_generator(task, subtasks_number):
    subtasks_coords = get_subtasks_coord(task, subtasks_number)
    crops = []
    #counter = 0
    for rect in subtasks_coords:
        crop = task.crop((rect.left, rect.top, rect.right, rect.bottom))
        crops.append(crop)
        #counter += 1
        #crop.save(str(counter) + ".png")
    return crops, subtasks_coords

def redundancy_generator(task, K, context, algorithm):
    coords = get_redundancy_coord(task, K, context, algorithm)
    crops = []
    #counter = 0
    for rect in coords:
        crop = task.crop((rect.left, rect.top, rect.right, rect.bottom))
        crops.append(crop)
        #counter += 1
        #rop.save(str(counter) + ".png")
    return crops, coords

def make_subtasks(images, coords):
    subtasks = []
    for img, coords in zip( images, coords):
        subtasks.append(Subtask(coords, img))
    return subtasks

if __name__ == '__main__':
    task = Image.open(test_path)
    subtasks_count = 12
    K = 2
    subtask_size = get_subtasks_size(task.height, subtasks_count)
    context = Context(task.width, subtask_size)
    subtasks, s_coords = subtasks_generator(task, subtasks_count)
    input = make_subtasks(subtasks, s_coords)
    redundancies, r_coords = redundancy_generator(task, K, context, get_redundancy_segment_random)
    input.extend(make_subtasks(redundancies, r_coords))
    conflicts = find_conflicts(input)