import math
import copy

CORES_MODE_CHANGES = [
  ['c1', 'c2'],
  ['c1', 'c3'],
  ['c1', 'c4'],
  ['c2', 'c3'],
  ['c2', 'c4'],
  ['c2', 'c1'],
  ['c3', 'c1'],
  ['c3', 'c2'],
  ['c3', 'c4'],
  ['c4', 'c1'],
  ['c4', 'c2'],
  ['c4', 'c3']
]

CORES_NO_MIGRATION = {
  'c1': {'tasks': [], 'considered': False, 'utilization': 0},
  'c2': {'tasks': [], 'considered': False, 'utilization': 0},
  'c3': {'tasks': [], 'considered': False, 'utilization': 0},
  'c4': {'tasks': [], 'considered': False, 'utilization': 0}
}

CORES_MODEL_1 = {
    'c1': {
      'tasks': [],
      'considered': False,
      'utilization': 0,
      'migration': [
        ['c2', 'c3']
      ]
    },
    'c2': {
      'tasks': [],
      'considered': False,
      'utilization': 0,
      'migration': [
        ['c3', 'c4']
      ]
    },
    'c3': {
      'tasks': [],
      'considered': False,
      'utilization': 0,
      'migration': [
        ['c4', 'c1']
      ]
    },
    'c4': {
      'tasks': [],
      'considered': False,
      'utilization': 0,
      'migration': [
        ['c1', 'c2']
      ]
    }
  }

def worst_fit_bin_packing (task, cores):
  min_utilization = 1
  result = None
  for c in cores:
    core = cores[c]
    if not core['considered'] and core['utilization'] + task['U'] < 1 and core['utilization'] < min_utilization:
      result = c
      min_utilization = core['utilization']
  return result

def findHp (i, tasks):
  result = []
  task = tasks[i]
  for j in range(len(tasks)):
    if j == i:
      continue
    other_task = tasks[j]
    if other_task['P'] < 0 or other_task['P'] > task['P']:
      result.append(other_task)
  return result

def findHpHI (i, tasks):
  result = []
  task = tasks[i]
  for j in range(len(tasks)):
    if j == i:
      continue
    other_task = tasks[j]
    if other_task['HI'] and (other_task['P'] < 0 or other_task['P'] > task['P']):
      result.append(other_task)
  return result

def findHpLO (i, tasks):
  result = []
  task = tasks[i]
  for j in range(len(tasks)):
    if j == i:
      continue
    other_task = tasks[j]
    if not other_task['HI'] and (other_task['P'] < 0 or other_task['P'] > task['P']):
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
  print('RTA_NO_MIG', len(tasks), tasks)
  for i in range(len(tasks)):
    task = tasks[i]
    hp = findHp(i, tasks)
    print(task['D'], len(hp))
    RiLO = calcRiLO(task, hp)
    print('RiLO', RiLO)
    if RiLO is None:
      return False
    if task['HI']:
      hpHI = findHpHI(i, tasks)
      hpLO = findHpLO(i, tasks)
      RiHI = calcRiHI(task, hpHI)
      print('RiHI', RiHI)
      if RiHI is None:
        return False
      RiHI_star = calcRiHI_star(task, hpHI, hpLO, RiLO)
      print('RiHI_star', RiHI_star)
      if RiHI_star is None:
        return False
  return True

def audsley_rta_no_migration (i, tasks):
  task = tasks[i]
  hp = findHp(i, tasks)
  RiLO = calcRiLO(task, hp)
  if RiLO is None:
    return False
  if task['HI']:
    hpHI = findHpHI(i, tasks)
    hpLO = findHpLO(i, tasks)
    RiHI = calcRiHI(task, hpHI)
    if RiHI is None:
      return False
    RiHI_star = calcRiHI_star(task, hpHI, hpLO, RiLO)
    if RiHI_star is None:
      return False
  return True

def find_lon_dead(tasks, HI):
  max_deadline = -1
  result = -1
  for i in range(len(tasks)):
    task = tasks[i]
    if task['P'] < 0 and task['HI'] == HI and task['D'] > max_deadline:
      max_deadline = task['D']
      result = i
  return result

def audsley_no_migration (core):
  priority_levels = len(core['tasks'])
  verification_tasks = copy.deepcopy(core['tasks'])
  for p_lvl in range(priority_levels):
    lon_dead_HI_i = find_lon_dead(verification_tasks, True)
    if lon_dead_HI_i >= 0:
      lon_dead_HI = verification_tasks[lon_dead_HI_i]
      lon_dead_HI['P'] = p_lvl
      if audsley_rta_no_migration(lon_dead_HI_i, verification_tasks):
        continue
      lon_dead_HI['P'] = -1
    lon_dead_LO_i = find_lon_dead(verification_tasks, False)
    if lon_dead_LO_i > 0:
      lon_dead_LO = verification_tasks[lon_dead_LO_i]
      lon_dead_LO['P'] = p_lvl
      if audsley_rta_no_migration(lon_dead_LO_i, verification_tasks):
        continue
      lon_dead_LO['P'] = -1
    return False
  return True

def verify_no_migration (taskset):
  global CORES_NO_MIGRATION
  cores = copy.deepcopy(CORES_NO_MIGRATION)
  for task in taskset:
    reset_considered(cores)
    assigned = False
    count = 0
    while not assigned and count < 4:
      count += 1
      next_core = worst_fit_bin_packing(task, cores)
      if next_core is not None:
        cores[next_core]['considered'] = True
        # Verify Response Time Analysis
        verification_core = copy.deepcopy(cores[next_core])
        verification_core['tasks'].append(task)
        if audsley_no_migration(verification_core):
          cores[next_core]['tasks'].append(task)
          cores[next_core]['utilization'] += task['U']
          assigned = True
    if not assigned:
      return False
  return True

def calcRi (task, hp):
  start_value = task['C(LO)']
  if task['HI']:
    start_value = task['C(HI)']
  Ri = start_value
  while True:
    newRi = start_value
    for hp_task in hp:
      multi_c = hp_task['C(LO)']
      if task['HI'] and hp_task['HI']:
        multi_c = hp_task['C(HI)']
      newRi += math.ceil(Ri / hp_task['D']) * multi_c
    if newRi > task['D']:
      return None
    if newRi == Ri:
      return newRi
    Ri = newRi

def rta_base (tasks):
  for task in tasks:
    hp = findHp(task, tasks)
    Ri = calcRi(task, hp)
    if Ri is None:
      return False
  return True

def reset_considered (cores):
  for c in cores:
    core = cores[c]
    core['considered'] = False

def verify_base (task, cores):
  assigned = False
  count = 0
  while not assigned and count < 4:
    count += 1
    next_core = worst_fit_bin_packing(task, cores)
    if next_core is not None:
      cores[next_core]['considered'] = True
      # Verify Response Time Analysis
      verification_core = copy.deepcopy(cores[next_core])
      verification_core['tasks'].append(task)
      if audsley_no_migration(verification_core):
        cores[next_core]['tasks'].append(task)
        cores[next_core]['utilization'] += task['U']
        assigned = True
  return assigned

def calcRiLO_SE (task, hp):
  RiLO = task['C(LO)']
  while True:
    newRiLO = task['C(LO)']
    for hp_task in hp:
      newRiLO += math.ceil(RiLO / hp_task['D']) * hp_task['C(LO)']
    if newRiLO > task['D']:
      return None
    if newRiLO == RiLO:
      # Update Jitter and Deadline
      task['J'] = task['J'] + (RiLO - task['C(LO)'])
      task['D1'] = task['D'] - (RiLO - task['C(LO)'])
      task['Ri(LO)'] = RiLO
      return newRiLO
    RiLO = newRiLO

def verify_steady (cores):
  for c in cores:
    core = cores[c]
    for task in core['tasks']:
      hp = findHp(task, core['tasks'])
      RiLO = calcRiLO_SE(task, hp)
      if RiLO is None:
        return False
  return True

def findCHp (task, core, tasks):
  result = []
  for other_task in tasks:
    if not other_task['migrating'] and (other_task['P'] > task['P']):
      result.append(other_task)
  return result

def findCHpHI (task, core, tasks):
  result = []
  for other_task in tasks:
    if other_task['HI'] and (other_task['P'] > task['P']):
      result.append(other_task)
  return result

def findCHpLO (task, core, tasks):
  result = []
  for other_task in tasks:
    if not other_task['HI'] and (other_task['P'] > task['P']):
      result.append(other_task)
  return result

def findCHpMIG (task, core, tasks):
  result = []
  for other_task in tasks:
    if (other_task['migrating'] and core not in other_task['migration_route']) and (other_task['P'] > task['P']):
      result.append(other_task)
  return result

def riMIXStep (task, chp, chpMIG):
  start_val = task['C(LO)']
  if task['HI']:
    start_val = task['C(HI)']
  RiMIX = start_val
  while True:
    newRiMIX = start_val
    for chp_task in chp:
      chp_val = chp_task['C(LO)']
      if chp_task['HI']:
        chp_val = chp_task['C(HI)']
      newRiMIX += math.ceil(RiMIX / chp_task['D']) * chp_val
    for chp_mig in chpMIG:
      newRiMIX += math.ceil(task['Ri(LO)'] / chp_mig['D']) * chp_mig['Ri(LO)']
    if newRiMIX > task['D']:
      return None
    if newRiMIX == RiMIX:
      return RiMIX
    RiMIX = newRiMIX

def riLO_1Step (task, chp, core):
  RiLO_1 = task['C(LO)']
  task_deadline = task['D']
  if (task['migrating'] and core in task['migration_route']):
    task_deadline = task['D1']
  while True:
    newRiLO_1 = task['C(LO)']
    for chp_task in chp:
      chp_jitter = 0
      chp_deadline = chp_task['D']
      if (chp_task['migrating'] and core in chp_task['migration_route']):
        chp_jitter = chp_task['J']
        chp_deadline = chp_task['D1']
      newRiLO_1 += math.ceil((RiLO_1 + chp_jitter) / chp_deadline) * chp_task['C(LO)']
    if newRiLO_1 > task_deadline:
      return None
    if newRiLO_1 == RiLO_1:
      task['J2'] = task['J'] + (RiLO_1 - task['C(LO)'])
      task['D2'] = task['D1'] - (RiLO_1 - task['C(LO)'])
      task['Ri(LO)'] = RiLO_1
      return RiLO_1
    RiLO_1 = newRiLO_1

def riHI_1Step (task, chpHI, chpLO, core):
  RiHI_1 = task['C(HI)']
  task_deadline = task['D']
  if (task['migrating'] and core == task['migration_route'][0]):
    task_deadline = task['D1']
  elif (task['migrating'] and core == task['migration_route'][1]):
    task_deadline = task['D2']
  while True:
    newRiHI_1 = task['C(HI)']
    for chp_task in chpHI:
      newRiHI_1 += math.ceil(RiHI_1 / chp_task['D']) * chp_task['C(HI)']
    for chp_task in chpLO:
      chp_jitter = 0
      chp_deadline = chp_task['D']
      if (chp_task['migrating'] and core == chp_task['migration_route'][0]):
        chp_jitter = chp_task['J']
        chp_deadline = chp_task['D1']
      elif (chp_task['migrating'] and core == chp_task['migration_route'][1]):
        chp_jitter = chp_task['J2']
        chp_deadline = chp_task['D2']
      newRiHI_1 += math.ceil((task['Ri(LO)'] + chp_jitter) / chp_deadline) * chp_task['C(LO)']
    if newRiHI_1 > task_deadline:
      return None
    if newRiHI_1 == RiHI_1:
      return RiHI_1
    RiHI_1 = newRiHI_1

def calcRiMIX (core, cores):
  for task in cores[core]['tasks']:
    if not task['migrating']:
      chp = findCHp(task, core, cores[core]['tasks'])
      chpMIG = findCHpMIG(task, core, cores[core]['tasks'])
      if riMIXStep(task, chp, chpMIG) is None:
        return False
  return True

def calcRiLO_1 (core, cores):
  for task in cores[core]['tasks']:
    #chp = findCHp(task, core, cores[core]['tasks'])
    chp = findHp(task, cores[core]['tasks'])
    if riLO_1Step(task, chp, core) is None:
      return False
  return True

def calcRiHI_1 (core, cores):
  for task in cores[core]['tasks']:
    if task['HI']:
      chpHI = findCHpHI(task, core, cores[core]['tasks'])
      chpLO = findCHpLO(task, core, cores[core]['tasks'])
      if riHI_1Step(task, chpHI, chpLO, core) is None:
        return False
  return True

def verify_mode_changes (cores):
  global CORES_MODE_CHANGES
  for mode_change in CORES_MODE_CHANGES:
    crit_count = 0
    verification_cores = copy.deepcopy(cores)
    for crit_core in mode_change:
      migration_cores = []
      new_crit_core_tasks = []
      for task in verification_cores[crit_core]['tasks']:
        if not task['migrating']:
          new_crit_core_tasks.append(task)
        else:
          # Always attempt to migrate to the first migration core
          migration_core = task['migration_route'][0]
          # If it is already in HI-crit mode, migrate to the second
          if crit_count > 0 and (migration_core == mode_change[0] or migration_core == crit_core):
            migration_core = task['migration_route'][1]
          verification_cores[migration_core]['tasks'].append(task)
          if migration_core not in migration_cores:
            migration_cores.append(migration_core)
      # RTA for new crit core
      if not calcRiMIX(crit_core, verification_cores):
        return False
      # Remove migrated tasks from crit_core
      verification_cores[crit_core]['tasks'] = new_crit_core_tasks
      # RTA for migration cores
      for m_c in migration_cores:
        if not calcRiLO_1(m_c, verification_cores):
          return False
      crit_count += 1
    for core in verification_cores:
      # Verify 3rd crit core
      if core not in mode_change:
        if not calcRiHI_1(core, verification_cores):
          return False
  return True

def verify_migration (task, cores):
  task['migrating'] = True
  assigned = False
  count = 0
  while not assigned and count < 4:
    count += 1
    next_core = worst_fit_bin_packing(task, cores)
    if next_core is not None:
      cores[next_core]['considered'] = True
      # Copy objects to avoid side effects
      verification_task = copy.deepcopy(task)
      verification_cores = copy.deepcopy(cores)
      verification_cores[next_core]['tasks'].append(verification_task)
      if verify_steady(verification_cores):
        for migration_group in cores[next_core]['migration']:
          verification_task['migration_route'] = migration_group
          # Verify mode changes
          if verify_mode_changes(verification_cores):
            assigned = True
            task['migration_route'] = migration_group
            cores[next_core]['tasks'].append(task)
            cores[next_core]['utilization'] += task['U']
            break
  reset_considered(cores)
  if not assigned:
    return False
  return True

def verify_model_1 (taskset):
  global CORES_MODEL_1
  cores = copy.deepcopy(CORES_MODEL_1)
  for task in taskset:
    if not verify_base(task, cores):
      if task['HI'] or not verify_migration(task, cores):
        return False
  return True

def verify_model_2 (taskset):
  pass

def verify_model_4 (taskset):
  pass