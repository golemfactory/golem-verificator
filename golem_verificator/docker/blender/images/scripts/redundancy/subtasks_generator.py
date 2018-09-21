from PIL import Image
from partitioning import get_subtasks_coord


def subtasks_generator(image_tasks_path, subtask_number):
    task = Image.open(image_tasks_path)
    subtasks_coord = get_subtasks_coord(task, subtask_number)
    return subtasks_coord

if __name__ == '__main__':
    for s in subtasks_generator('barcelona_[samples=8725].png', 12):
        print(s)
