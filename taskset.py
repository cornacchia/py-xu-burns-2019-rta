import numpy
import math
import random
import functools

# Default values taken from "Techniques For The Synthesis Of Multiprocessor Tasksets" by Emberson, et. al
# cfr. https://www.researchgate.net/publication/241677949_Techniques_For_The_Synthesis_Of_Multiprocessor_Tasksets
def log_uniform (n, Tmin = 10, Tmax = 1000, Tg = 10):
  R = numpy.random.uniform(math.log(Tmin), math.log(Tmax + Tg), n)
  T = []
  for ri in R:
    T.append(math.floor(math.exp(ri) / Tg) * Tg)
  return T

def UUnifast_discard_step (n, maxU):
  sumU = maxU
  U = []
  for i in range (1, n):
    nextSumU = sumU * (numpy.random.uniform() ** (1 / (n - i)))
    U.append(sumU - nextSumU)
    sumU = nextSumU
  U.append(sumU)
  # "Discard" step, if one of the utilizations is > 1 drop all the results
  for i in range(0, n):
    if (U[i] > 1):
      return False, None
  return True, U

def UUnifast_discard (n, maxU):
  flag, U = UUnifast_discard_step(n, maxU)
  while not flag:
    flag, U = UUnifast_discard_step(n, maxU)
  return U

# Sort by criticality first, then utilization
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

# n -> Taskset size
# p -> Percentage of HI-crit tasks
# f -> Criticality factor
# maxU -> Total taskset utilization
def generate_taskset (n, p, f, maxU):
  HI_tot = n * p
  LO_tot = n - HI_tot
  U = UUnifast_discard(n, maxU)
  T = log_uniform(n)
  taskset = []
  for i in range(n):
    new_task = {
      # Is this task HI-crit?
      'HI': False,
      # HI-crit WCET
      'C(HI)': -1,
      # LO-crit WCET
      'C(LO)': -1,
      # Nominal utilization
      'U': U[i],
      # Deadline (== Period)
      'D': T[i],
      # Jitter
      'J': 0,
      # Is this task migratable?
      'migrating': False,
      # Which migration route does this task follow?
      'migration_route': [],
      # Priorities for each core
      'P': {'c1': -1, 'c2': -1, 'c3': -1, 'c4': -1}
      }
    # Randomly set tasks as HI-crit (but always respect the percentage of HI-crit tasks "p")
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
      LO_tot -= 1
    taskset.append(new_task)
  # Sort by criticality and utilization
  taskset.sort(key=functools.cmp_to_key(sort_tasks_criticality))
  return taskset

def calc_total_utilization (taskset):
  result = 0
  for task in taskset:
    result += task['U']
  return result