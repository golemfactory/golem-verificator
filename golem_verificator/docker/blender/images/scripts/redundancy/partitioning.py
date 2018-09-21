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

def get_redundacy_segment_vertical_ordered(redundancy_area, subtask, dimension):
    segments_number = math.ceil(redundancy_area / subtask.area)
    rects = []
    new_width = subtask.height * subtask.width / dimension 
    for i in range(0, segments_number):
        left = i * new_width
        right = left + new_width
        top = 0
        bottom = dimension
        rect = Rectangle(left, right, top, bottom)
        rects.append(rect)
    return rects

def get_redundancy_segment_random(K, subtasks_count, subtask, height, width):
    segments_number = K * subtasks_count
    rects = []
    new_width = subtask.height * subtask.width / height
    for i in range(0, int(segments_number)):
        start_range = i * new_width
        end_range = start_range + new_width / 2
        left = random.randint(int(start_range), int(end_range))
        right = left + new_width
        top = 0
        bottom = height
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
    redundant_segments = []

    # whole_times = int(redundancy_area // area)
    
    # if whole_times != 0:
    #     for i in range(0,whole_times):
    #         redundant_segments.extend(get_redundacy_segment_vertical_ordered(area, subtask, task.height))
    # if redundancy_area % area != 0:
    #     redundant_segments.extend(get_redundacy_segment_vertical_ordered(redundancy_area % area, subtask, task.height))        
            
    part_k, whole_ks = math.modf(K-1)
    if whole_ks != 0:
        for i in range(1, int(whole_ks)+1):
            redundant_segments.extend(get_redundancy_segment_random(i, subtasks_count, subtask, task.height, task.width))
        
    if part_k != 0:
        redundant_segments.extend(get_redundancy_segment_random(part_k, subtasks_count, subtask, task.height, task.width))

    return redundant_segments
    #return subtasks

if __name__ == '__main__':
    subtasks = task_partitioning(Task(800,600), 12, 2.5)
    for s in subtasks:
        print(s)