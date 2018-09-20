from fractions import Fraction
import math
import random
from subtask import Rectangle

class Task:

    def __init__(self, width, height):
        self.width = width
        self.height = height


class Subtask:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.area = width * height
        self.aspect_ratio = width / height

def get_redundacy_segment(redundancy_area, subtask, dimension):
    segments_number = math.ceil(redundancy_area / subtask.area)
    rects = []
    new_width = subtask.height * subtask.width / dimension
    zone_width = subtask.width / segments_number
    for i in range(0, segments_number):
        left_base = i * zone_width
        left = left_base + random.random() * ( zone_width - new_width )
        right = left + new_width
        top = 0
        bottom = dimension
        rect = Rectangle(left, right, top, bottom)
        rects.append(rect)
    return rects

def task_partitioning(task, subtasks_count, K):
    subtask_size = Fraction(task.height, subtasks_count)

    subtask = Subtask(task.width, subtask_size)

    subtasks = []

    for i in range(0, subtasks_count):
        left = 0
        right = task.width
        top = i * subtask_size
        bottom = top + subtask_size
        rect = Rectangle(left, right, top, bottom)
        subtasks.append(rect)

    area = task.height * task.width
    redundancy_area = area * K - area

    whole_times = int(redundancy_area // area)
    
    redundant_segments = []
    
    if whole_times != 0:
        for i in range(0,whole_times):
            redundant_segments.extend(get_redundacy_segment(area, subtask, task.height))
        
    if redundancy_area % area != 0:
        redundant_segments.extend(get_redundacy_segment(redundancy_area % area, subtask, task.height))

    return redundant_segments
    #return subtasks

if __name__ == '__main__':
    subtasks = task_partitioning(Task(800,600), 13, 1.5)
    for s in subtasks:
        print(s)