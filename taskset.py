import numpy
import math
import random
import functools

def log_uniform (n, Tmin = 10, Tmax = 1000, Tg = 10):
  R = numpy.random.uniform(math.log(Tmin), math.log(Tmax + Tg), n)
  T = []
  for ri in R:
    T.append(math.floor(math.exp(ri) / Tg) * Tg)
  return T

def UUnifast_discard_step (n, maxU):
  R = numpy.random.uniform(0, 1, n)
  S = [0] * (n + 1)
  S[n] = maxU
  U = []
  for i in range(n, 1, -1):
    S[i - 1] = S[i] * (R[i - 1] ** (1 / (i - 1)))
  for i in range(1, n + 1):
    U.append(S[i] - S[i - 1])
  # Discard step
  for i in range(0, n):
    if (U[i] > 1):
      return False, None
  return True, U

def UUnifast_discard (n, maxU):
  flag, U = UUnifast_discard_step(n, maxU)
  while not flag:
    flag, U = UUnifast_discard_step(n, maxU)
  return U

def sort_tasks_criticality (t1, t2):
  if t1['HI'] and not t2['HI']:
    return -1
  elif not t1['HI'] and t2['HI']:
    return 1
  else:
    if t1['U'] >= t2['U']:
      return -1
    else:
      return 1

def sort_tasks_period (t1, t2):
  if t1['D'] >= t2['D']:
    return -1
  return 1

def generate_taskset (n, p, f, maxU):
  HI_tot = n * p
  LO_tot = n - HI_tot
  U = UUnifast_discard(n, maxU)
  T = log_uniform(n)
  taskset = []
  for i in range(n):
    new_task = {'HI': False, 'C(HI)': -1, 'C(LO)': -1, 'U': U[i], 'D': T[i], 'J': 0}
    HI_flag = random.choice([True, False])
    if HI_flag and HI_tot <= 0:
      HI_flag = False
    if not HI_flag and LO_tot <= 0:
      HI_flag = True
    if HI_flag:
      HI_tot -= 1
      new_task['HI'] = True
      new_task['C(HI)'] = U[i] * T[i]
      new_task['C(LO)'] = new_task['C(HI)'] / f
    else:
      new_task['C(LO)'] = U[i] * T[i]
    taskset.append(new_task)
  # Assign RM priority
  taskset.sort(key=functools.cmp_to_key(sort_tasks_period))
  for i in range(len(taskset) - 1, -1, -1):
    taskset[i]['P'] = i
  # Sort by criticality and utilization
  taskset.sort(key=functools.cmp_to_key(sort_tasks_criticality))
  return taskset

def calc_total_utilization (taskset):
  result = 0
  for task in taskset:
    result += task['U']
  return result