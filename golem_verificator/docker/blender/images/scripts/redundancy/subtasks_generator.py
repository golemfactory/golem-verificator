import os
from PIL import Image
from partitioning import get_subtasks_coord
from partitioning import get_redundancy_segment_random
from partitioning import get_redundancy_coord
from partitioning import Subtask, get_subtasks_size

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

def redundancy_generator(task, K, subtask, algorithm):
    coords = get_redundancy_coord(task, K, subtask, algorithm)
    crops = []
    #counter = 0
    for rect in coords:
        crop = task.crop((rect.left, rect.top, rect.right, rect.bottom))
        crops.append(crop)
        #counter += 1
        #rop.save(str(counter) + ".png")
    return crops, coords

if __name__ == '__main__':
    task = Image.open(test_path)
    subtasks_count = 12
    K = 2
    subtask_size = get_subtasks_size(task.height, subtasks_count)
    subtask = Subtask(task.width, subtask_size)
    subtasks, s_coords = subtasks_generator(task, subtasks_count)
    redundancies, r_coords = redundancy_generator(task, K, subtask, get_redundancy_segment_random)
