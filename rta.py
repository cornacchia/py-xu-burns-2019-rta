import math

def worst_fit_bin_packing (task, cores):
  min_utilization = 1
  result = None
  for c in cores:
    core = cores[c]
    if not core['considered'] and core['utilization'] + task['U'] < 1 and core['utilization'] < min_utilization:
      result = c
      min_utilization = core['utilization']
  return result

def findHp (task, tasks):
  result = []
  for other_task in tasks:
    if other_task['P'] > task['P']:
      result.append(other_task)
  return result

def findHpHI (task, tasks):
  result = []
  for other_task in tasks:
    if other_task['HI'] and other_task['P'] > task['P']:
      result.append(other_task)
  return result

def findHpLO (task, tasks):
  result = []
  for other_task in tasks:
    if not other_task['HI'] and other_task['P'] > task['P']:
      result.append(other_task)
  return result

def calcRiLO (task, hp):
  RiLO = task['C(LO)']
  while True:
    newRiLO = task['C(LO)']
    for hp_task in hp:
      newRiLO += math.ceil(RiLO / hp_task['D']) * hp_task['C(LO)']
    if newRiLO > task['D']:
      return None
    if newRiLO == RiLO:
      return newRiLO
    RiLO = newRiLO

def calcRiHI (task, hpHI):
  RiHI = task['C(HI)']
  while True:
    newRiHI = task['C(HI)']
    for hp_task in hpHI:
      newRiHI += math.ceil(RiHI / hp_task['D']) * hp_task['C(HI)']
    if newRiHI > task['D']:
      return None
    if newRiHI == RiHI:
      return newRiHI
    RiHI = newRiHI

def calcRiHI_star (task, hpHI, hpLO, RiLO):
  RiHI_star = task['C(HI)']
  while True:
    newRiHI_star = task['C(HI)']
    for hp_task in hpHI:
      newRiHI_star += math.ceil(RiHI_star / hp_task['D']) * hp_task['C(HI)']
    for hp_task in hpLO:
      newRiHI_star += math.ceil(RiLO / hp_task['D']) * hp_task['C(LO)']
    if newRiHI_star > task['D']:
      return None
    if newRiHI_star == RiHI_star:
      return newRiHI_star
    RiHI_star = newRiHI_star

def rta_no_migration (tasks):
  for task in tasks:
    hp = findHp(task, tasks)
    RiLO = calcRiLO(task, hp)
    if RiLO is None:
      return False
    if task['HI']:
      hpHI = findHpHI(task, tasks)
      hpLO = findHpLO(task, tasks)
      RiHI = calcRiHI(task, hpHI)
      if RiHI is None:
        return False
      RiHI_star = calcRiHI_star(task, hpHI, hpLO, RiLO)
      if RiHI_star is None:
        return False
  return True


def verify_no_migration (taskset):
  cores = {
    'c1': {'tasks': [], 'considered': False, 'utilization': 0},
    'c2': {'tasks': [], 'considered': False, 'utilization': 0},
    'c3': {'tasks': [], 'considered': False, 'utilization': 0},
    'c4': {'tasks': [], 'considered': False, 'utilization': 0}
  }
  for task in taskset:
    for c in cores:
      core = cores[c]
      core['considered'] = False
    assigned = False
    count = 0
    while not assigned and count < 4:
      count += 1
      next_core = worst_fit_bin_packing(task, cores)
      if next_core is not None:
        cores[next_core]['considered'] = True
        # Verify Response Time Analysis
        tasks = cores[next_core]['tasks'].copy()
        tasks.append(task)
        if rta_no_migration (tasks):
          cores[next_core]['tasks'].append(task)
          cores[next_core]['utilization'] += task['U']
          assigned = True
    if not assigned:
      return False
  return True

def rta_base (tasks):
  pass

def verify_model_1 (taskset):
  cores = {
    'c1': {'tasks': [], 'considered': False, 'utilization': 0},
    'c2': {'tasks': [], 'considered': False, 'utilization': 0},
    'c3': {'tasks': [], 'considered': False, 'utilization': 0},
    'c4': {'tasks': [], 'considered': False, 'utilization': 0}
  }
  for task in taskset:
    for c in cores:
      core = cores[c]
      core['considered'] = False
    assigned = False
    count = 0
    while not assigned and count < 4:
      count += 1
      next_core = worst_fit_bin_packing(task, cores)
      if next_core is not None:
        cores[next_core]['considered'] = True
        # Verify Response Time Analysis
        tasks = cores[next_core]['tasks'].copy()
        tasks.append(task)
        if rta_base (tasks):
          cores[next_core]['tasks'].append(task)
          cores[next_core]['utilization'] += task['U']
          assigned = True
    if not assigned and not task['HI']:
      # Try to assign migratable
      for c in cores:
        core = cores[c]
        core['considered'] = False
      assigned = False
      count = 0
      while not assigned and count < 4:
        count += 1
        next_core = worst_fit_bin_packing(task, cores)
        if next_core is not None:
          cores[next_core]['considered'] = True
          # Verify Response Time Analysis
          tasks = cores[next_core]['tasks'].copy()
          tasks.append(task)
          if rta_base (tasks):
            cores[next_core]['tasks'].append(task)
            cores[next_core]['utilization'] += task['U']
            assigned = True
  return True

def verify_model_2 (taskset):
  pass

def verify_model_4 (taskset):
  pass

def verify_taskset (taskset):
  pass
