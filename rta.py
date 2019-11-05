import sys
import math
import copy
import functools
import config

# Reset "considered" flag on cores
# This is invoked when a new task is selected for scheduling
def reset_considered (cores):
  for c in cores:
    core = cores[c]
    core['considered'] = False

# Implements the first fit bin-packing algorithm
# To use it set config.FIRST_FIT_BP to True
def first_fit_bin_packing (task, cores):
  for c in cores:
    core = cores[c]
    if not core['considered'] and core['utilization'] + task['U'] <= 1:
      return c
  return None

# Implements the first fit bin-packing algorithm
# To use it set config.WORST_FIT_BP to True
def worst_fit_bin_packing (task, cores):
  min_utilization = 1
  result = None
  for c in cores:
    core = cores[c]
    if not core['considered'] and core['utilization'] < min_utilization:
      result = c
      min_utilization = core['utilization']
  return result

# Get the next core to check according to the algorithm specified in the config
def get_next_core (task, cores):
  if config.FIRST_FIT_BP:
    return first_fit_bin_packing(task, cores)
  elif config.WORST_FIT_BP:
    return worst_fit_bin_packing(task, cores)
  else:
    print('!!! ERROR: No bin-packing algorithm selected !!!')
    sys.exit()

# Find tasks with priority greater than Ti's (= tasks[i]) priority
def findHp (i, tasks, core):
  result = []
  task = tasks[i]
  for j in range(len(tasks)):
    if j == i:
      continue
    other_task = tasks[j]
    if other_task['P'][core] < 0 or other_task['P'][core] > task['P'][core]:
      result.append(other_task)
  return result

# Vestal's algorithm
def calcRi (task, hp):
  start_Ri = task['C(LO)']
  if task['HI']:
    start_Ri = task['C(HI)']
  Ri = start_Ri
  while True:
    newRi = start_Ri
    for hp_task in hp:
      hp_C = hp_task['C(LO)']
      if task['HI'] and hp_task['HI']:
        hp_C = hp_task['C(HI)']
      newRi += math.ceil(Ri / hp_task['D']) * hp_C
    if newRi > task['D']:
      return None
    if newRi == Ri:
      return newRi
    Ri = newRi

def audsley_rta_no_migration (i, tasks, core, core_id):
  task = tasks[i]
  hp = findHp(i, tasks, core_id)
  Ri = calcRi(task, hp)
  if Ri is None:
    return False
  return True

# Find which task, in this core, has the longest deadline
# core -> core on which we are checking
# tasks -> core's tasks
# HI -> should we check HI-crit tasks or LO-crit tasks?
def find_lon_dead(core, tasks, HI):
  max_deadline = -1
  result = -1
  for i in range(len(tasks)):
    task = tasks[i]
    # Ensure that the task doesn't already have a priority for this core
    if task['P'][core] < 0 and task['HI'] == HI and task['D'] > max_deadline:
      max_deadline = task['D']
      result = i
  return result

# Implements Audsley's OPA
# core -> core object
# core_id -> core identifier
# audsley_rta -> RTA algorithm to use (no migration, Ri(LO), Ri(HI), etc.)
# side_effect -> Should the priorities assigned during this step be saved?
def audsley (core, core_id, audsley_rta, side_effect):
  # One priority for each task
  priority_levels = len(core['tasks'])
  # Clone tasks to avoid side effects
  verification_tasks = copy.deepcopy(core['tasks'])
  for p_lvl in range(priority_levels):
    # Find the HI-crit task with greatest deadline (and no priority for this core)
    lon_dead_HI_i = find_lon_dead(core_id, verification_tasks, True)
    if lon_dead_HI_i >= 0:
      lon_dead_HI = verification_tasks[lon_dead_HI_i]
      lon_dead_HI['P'][core_id] = p_lvl
      # Check if system schedulable with p_lvl priority assinged to to this task
      lon_dead_HI_result = audsley_rta(lon_dead_HI_i, verification_tasks, core, core_id)
      # If the result is True skip the next check and leave the priority assigned to the task
      if lon_dead_HI_result:
        continue
      # Otherwise reset the priority and check LO-crit tasks
      lon_dead_HI['P'][core_id] = -1
    # Find the LO-crit task with greatest deadline (and no priority for this core)
    lon_dead_LO_i = find_lon_dead(core_id, verification_tasks, False)
    if lon_dead_LO_i >= 0:
      lon_dead_LO = verification_tasks[lon_dead_LO_i]
      lon_dead_LO['P'][core_id] = p_lvl
      lon_dead_LO_result = audsley_rta(lon_dead_LO_i, verification_tasks, core, core_id)
      if lon_dead_LO_result:
        continue
      lon_dead_LO['P'][core_id] = -1
    return False
  # In some cases we want to remember the priorities assigned at this point
  if side_effect:
    core['tasks'] = verification_tasks
  return True

def verify_no_migration_task (task, cores):
  # Cleanup "considered" flag on cores to start fresh for the new task
  reset_considered(cores)
  assigned = False
  count = 0
  while not assigned and count < 4:
    count += 1
    next_core = get_next_core(task, cores)
    if next_core is not None:
      cores[next_core]['considered'] = True
      # Always clone cores to avoid side effects
      verification_core = copy.deepcopy(cores[next_core])
      verification_core['tasks'].append(task)
      # Check core schedulability with Audsley's OPA
      if audsley(verification_core, next_core, audsley_rta_no_migration, False):
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

def findCHp (task, core, tasks, core_id):
  result = []
  for other_task in tasks:
    if not other_task['migrating'] and (other_task['P'][core_id] > task['P'][core_id]):
      result.append(other_task)
  return result

def findCHpHI (task, core, tasks, core_id):
  result = []
  for other_task in tasks:
    if other_task['HI'] and (other_task['P'][core_id] > task['P'][core_id]):
      result.append(other_task)
  return result

def findCHpLO (task, core, tasks, core_id):
  result = []
  for other_task in tasks:
    if not other_task['HI'] and (other_task['P'][core_id] > task['P'][core_id]):
      result.append(other_task)
  return result

def findCHpMIG (task, core, tasks):
  result = []
  for other_task in tasks:
    if (other_task['migrating'] and core not in other_task['migration_route']) and (other_task['P'][core] > task['P'][core]):
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
      if ('J' in task):
        task['J2'] = task['J'] + (RiLO_1 - task['C(LO)'])
      if ('D1' in task):
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

def audsleyRiMIX (i, tasks, core, core_id):
  task = tasks[i]
  if not task['migrating']:
    chp = findCHp(task, core, tasks, core_id)
    chpMIG = findCHpMIG(task, core, tasks)
    if riMIXStep(task, chp, chpMIG) is None:
      return False
  return True

def verify_RiMIX (core, core_id):
  for i in range(len(core['tasks'])):
    if not audsleyRiMIX(i, core['tasks'], core_id, core_id):
      return False
  return True

def audsleyRiLO_1 (i, tasks, core, core_id):
  task = tasks[i]
  chp = findHp(i, tasks, core_id)
  if riLO_1Step(task, chp, core) is None:
    return False
  return True

def audsleyRiHI_1 (i, tasks, core, core_id):
  task = tasks[i]
  if task['HI']:
    chpHI = findCHpHI(task, core, tasks, core_id)
    chpLO = findCHpLO(task, core, tasks, core_id)
    if riHI_1Step(task, chpHI, chpLO, core) is None:
      return False
  return True

def verifyRiHI_1 (core, core_id):
  for i in range(len(core['tasks'])):
    if not audsleyRiHI_1(i, core['tasks'], core_id, core_id):
      return False
  return True

def verify_mode_changes (cores):
  for mode_change in config.CORES_MODE_CHANGES:
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
      if not verify_RiMIX(verification_cores[crit_core], crit_core):
      #if not audsley(verification_cores[crit_core], crit_core, audsleyRiMIX, False):
        #print('no RiMIX')
        return False
      # Remove migrated tasks from crit_core
      verification_cores[crit_core]['tasks'] = new_crit_core_tasks
      # RTA for migration cores
      for m_c in migration_cores:
        if not audsley(verification_cores[m_c], m_c, audsleyRiLO_1, True):
          #print('no RiLO1')
          return False
      crit_count += 1
    for core in verification_cores:
      # Verify 3rd crit core
      if core not in mode_change:
        if not verifyRiHI_1(verification_cores[crit_core], crit_core):
        #if not audsley(verification_cores[core], core, audsleyRiHI_1, False):
          #print('no RiHI1')
          return False
  #print('TRUE')
  return True

def audsley_rta_steady (i, tasks, core, core_id):
  task = tasks[i]
  hp = findHp(i, tasks, core_id)
  RiLO = calcRiLO_SE(task, hp)
  if RiLO is None:
    return False
  return True

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

def get_LO_crit_tasks (tasks, core):
  result = []
  for i in range(len(tasks)):
    task = tasks[i]
    if not task['HI'] and not task['migrating']:
      result.append([i, task])
  if core == 'c1':
    result.sort(key=functools.cmp_to_key(sort_tasks_priority_c1))
  elif core == 'c2':
    result.sort(key=functools.cmp_to_key(sort_tasks_priority_c2))
  elif core == 'c3':
    result.sort(key=functools.cmp_to_key(sort_tasks_priority_c3))
  elif core == 'c4':
    result.sort(key=functools.cmp_to_key(sort_tasks_priority_c4))
  return [r[0] for r in result]

def backup_priorities (tasks):
  result = []
  for task in tasks:
    result.append(task['P'])
  return result

def assign_backup_priorities(core, bkp_priorities):
  for i in range(len(core['tasks'])):
    core['tasks'][i]['P'] = bkp_priorities[i]

def verify_migration_task (task, cores):
  reset_considered(cores)
  assigned = False
  count = 0
  while not assigned and count < 4:
    count += 1
    next_core = get_next_core(task, cores)
    if next_core is not None:
      cores[next_core]['considered'] = True
      verification_task = copy.deepcopy(task)
      verification_cores = copy.deepcopy(cores)
      verification_core = verification_cores[next_core]
      verification_core['tasks'].append(verification_task)
      if audsley(verification_core, next_core, audsley_rta_steady, True):
        # Tasks verified for steady mode, with priority and RiLO, C(LO), etc.
        LO_crit_tasks = get_LO_crit_tasks(verification_core['tasks'], next_core)
        assigned_migrating = False
        priorities_backup = backup_priorities(verification_core['tasks'])
        for LO_crit_task_i in LO_crit_tasks:
          verification_cores_mode = copy.deepcopy(verification_cores)
          assign_backup_priorities(verification_cores_mode[next_core], priorities_backup)
          verification_task_mode = verification_cores_mode[next_core]['tasks'][LO_crit_task_i]
          for migration_group in cores[next_core]['migration']:
            verification_task_mode['migrating'] = True
            verification_task_mode['migration_route'] = migration_group
            # Verify mode changes
            if verify_mode_changes(verification_cores_mode):
              assigned_migrating = True
              assigned = True
              cores[next_core]['tasks'].append(task)
              cores[next_core]['utilization'] += task['U']
              migrating_task = cores[next_core]['tasks'][LO_crit_task_i]
              migrating_task['migrating'] = True
              migrating_task['migration_route'] = migration_group
              break
          if assigned_migrating:
            break
        if assigned_migrating:
          break
  if not assigned:
    return False
  return True

# Point of entry for all the tests
# 1. No migration model: Vestal's algorithm
# 2. Model 1: 1 migration route for every core
# 3. Model 2: 2 migration routes for every core
# 4. Model 3: 6 migration routes for every core

def verify_no_migration (taskset):
  cores = copy.deepcopy(config.CORES_NO_MIGRATION)
  for task in taskset:
    if not verify_no_migration_task(task, cores):
      return False
  return True

def verify_model_1 (taskset):
  cores = copy.deepcopy(config.CORES_MODEL_1)
  for task in taskset:
    # Attempt assigning with no migration
    if not verify_no_migration_task(task, cores):
      # Otherwise attempt migration
      if task['HI'] or not verify_migration_task(task, cores):
        return False
  return True

def verify_model_2 (taskset):
  cores = copy.deepcopy(config.CORES_MODEL_2)
  for task in taskset:
    # Attempt assigning with no migration
    if not verify_no_migration_task(task, cores):
      # Otherwise attempt migration
      if task['HI'] or not verify_migration_task(task, cores):
        return False
  return True

def verify_model_3 (taskset):
  cores = copy.deepcopy(config.CORES_MODEL_3)
  for task in taskset:
    # Attempt assigning with no migration
    if not verify_no_migration_task(task, cores):
      # Otherwise attempt migration
      if task['HI'] or not verify_migration_task(task, cores):
        return False
  return True