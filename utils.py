# Define sorting functions for each core to be given to the standard list sorting function
def sort_tasks_priority_c1 (t1, t2):
  if t1[1]['P']['c1'] >= t2[1]['P']['c1']:
    return -1
  else:
    return 1

def sort_tasks_priority_c2 (t1, t2):
  if t1[1]['P']['c2'] >= t2[1]['P']['c2']:
    return -1
  else:
    return 1

def sort_tasks_priority_c3 (t1, t2):
  if t1[1]['P']['c3'] >= t2[1]['P']['c3']:
    return -1
  else:
    return 1

def sort_tasks_priority_c4 (t1, t2):
  if t1[1]['P']['c4'] >= t2[1]['P']['c4']:
    return -1
  else:
    return 1