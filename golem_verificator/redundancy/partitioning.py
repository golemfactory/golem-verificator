from fractions import Fraction
import math
import random
from subtask import Rectangle

class Context:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.area = width * height
        self.aspect_ratio = width / height

def get_redundacy_segment_vertical_ordered(segments_count, subtask_context, height):
    rects = []
    new_width = subtask_context.height * subtask_context.width / height
    for i in range(0, segments_count):
        left = i * new_width
        right = left + new_width
        top = 0
        bottom = height
        rect = Rectangle(left, right, top, bottom)
        rects.append(rect)
    return rects

def get_redundancy_segment_random(segments_count, subtask_context, height):
    rects = []
    new_width = subtask_context.height * subtask_context.width / height
    zone_width = subtask_context.width / segments_count
    for i in range(0, segments_count):
        left_base = i * zone_width
        left = left_base + math.ceil(random.random() * ( zone_width - new_width) )
        right = left + new_width
        top = 0
        bottom = height
        rect = Rectangle(left, right, top, bottom)
        rects.append(rect)
    return rects

def get_subtasks_size(task_height, subtasks_count):
    return Fraction(task_height, subtasks_count)

def get_subtasks_coord(task, subtasks_count):
    subtask_size = get_subtasks_size(task.height, subtasks_count)
    subtasks = []
    for i in range(0, subtasks_count):
        left = 0
        right = task.width
        top = i * subtask_size
        bottom = top + subtask_size
        rect = Rectangle(left, right, top, bottom)
        subtasks.append(rect)
    return subtasks

def get_redundancy_coord(task_context, K, subtasks_count, subtask_context, algorithm):
    whole_times = int(K)
    redundant_segments = []

    if whole_times > 1:
        for _ in range(1,whole_times):
            redundant_segments.extend(algorithm(subtasks_count, subtask_context, task_context.height))
    if K-whole_times != 0:
        redundant_segments.extend(algorithm(math.ceil((K-whole_times)* subtasks_count), subtask_context, task_context.height))
    
    return redundant_segments

def task_partitioning(task_context, subtasks_count, K, algorithm):
    subtask_size = get_subtasks_size(task_context.height, subtasks_count)

    subtasks = []
    subtasks.extend(get_subtasks_coord(task_context, subtasks_count))

    subtask_context = Context(task_context.width, subtask_size)
    redundant_segments = []
    redundant_segments.extend(get_redundancy_coord(task_context, K, subtasks_count, subtask_context, algorithm))
      
    return subtasks, redundant_segments

if __name__ == '__main__':
    subtasks, redundant_segments = task_partitioning(Context(800,600), 12, 1.9, get_redundancy_segment_random)
    for s in redundant_segments:
        print(s)

    # print("//////////////////////////")
    # subtasks, redundant_segments = task_partitioning(Task(800,600), 12, 1.9, get_redundacy_segment_vertical_ordered)
    # for s in redundant_segments:
    #     print(s)

    for s in subtasks:
        print(s)