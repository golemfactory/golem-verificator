import os
from PIL import Image
from partitioning import get_subtasks_coord


def subtasks_generator(image_tasks_path, subtasks_number):
    task = Image.open(image_tasks_path)
    subtasks_coords = get_subtasks_coord(task, subtasks_number)
    crops = []
    #counter = 0
    for rect in subtasks_coords:
        crop = task.crop((rect.left, rect.top, rect.right, rect.bottom))
        crops.append(crop)
        #counter += 1
        #crop.save(str(counter) + ".png")
    return crops

if __name__ == '__main__':
    subtasks_generator(os.path.normpath('/home/elfoniok/golem-verificator/golem_verificator/docker/blender/images/scripts/redundancy/barcelona_[samples=8725].png'), 12)
