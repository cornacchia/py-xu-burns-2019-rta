import numpy
import math
import random

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
  print(U)
  return U

def generate_taskset (n, p, f, maxU):
  HI_tot = n * p
  LO_tot = n - HI_tot
  U = UUnifast_discard(n, maxU)
  T = log_uniform(n)
  taskset = []
  for i in range(n):
    new_task = {'HI': False, 'C(HI)': -1, 'C(LO)': -1, 'U': U[i], 'P': 0, 'D': T[i], 'J': 0}
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
      new_task['P'] = 1
    else:
      new_task['C(LO)'] = U[i] * T[i]
      new_task['P'] = 0
    # TODO: test with random priority for all tasks
    taskset.append(new_task)
  return taskset

print(generate_taskset(24, 0.5, 2, 3.2))


