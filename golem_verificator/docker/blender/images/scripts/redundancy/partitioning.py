from fractions import Fraction
import math
import random
from subtask import Rectangle

class Task:

    def __init__(self, width, height):
        self.width = width
        self.height = height


def get_redundacy_segment(redundancy_area, subtask_area, dimesnion):
    segments_number = math.ceil(redundancy_area / subtask_area)
    #for i in range(0,segments_number):



def task_partitioning(task, subtasks_count, K):
    subtask_size = Fraction(task.height, subtasks_count)
    area = task.height * task.width
    subtask_area = area * subtask_size

    subtasks = []

    for i in range(0, subtasks_count):
        left = 0
        right = task.width
        top = i * subtask_size
        bottom = top + subtask_size
        rect = Rectangle(left, right, top, bottom)
        subtasks.append(rect)

    return subtasks

    # redundancy_area = area * K - area

    # whole_times = redundancy_area // area
    # for i in range(0,whole_times):
    #     get_redundacy_segment(area, subtask_area, task.width)
    
    # if redundancy_area % area != 0:
    #     get_redundacy_segment(redundancy_area % area, subtask_area, task.width)

if __name__ == '__main__':
    subtasks = task_partitioning(Task(800,600), 12, 1)
    for s in subtasks:
        print(s)