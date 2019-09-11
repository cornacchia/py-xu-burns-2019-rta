from taskset import generate_taskset, calc_total_utilization
from rta import verify_no_migration, verify_model_1, verify_model_2, verify_model_3
from plot import plot_data
import copy

NO_MIG = True
MODEL_1 = True
MODEL_2 = True
MODEL_3 = True

def run_first ():
  global NO_MIG, MODEL_1, MODEL_2, MODEL_3
  res_global = [[], [], [], []]
  U = 3.2
  step = 0.028
  number_of_tests = 100
  while U <= 4.6:
    print(U)
    res_local = [[U, 0], [U, 0], [U, 0], [U, 0]]
    for n_task in range(number_of_tests):
      new_taskset = generate_taskset(24, 0.5, 2, U)
      if NO_MIG and verify_no_migration(copy.deepcopy(new_taskset)):
        for i in range(4):
          res_local[i][1] += 1
      else:
        if MODEL_1 and verify_model_1(copy.deepcopy(new_taskset)):
          res_local[1][1] += 1
        if MODEL_2 and verify_model_2(copy.deepcopy(new_taskset)):
          res_local[2][1] += 1
        if MODEL_3 and verify_model_3(copy.deepcopy(new_taskset)):
          res_local[3][1] += 1
    for i in range(4):
      res_local[i][1] = res_local[i][1] * 100 / number_of_tests
      res_global[i].append(res_local[i])
    U += step
  data_to_plot = []
  if NO_MIG:
    data_to_plot.append({'label': 'No Migration', 'data': res_global[0]})
  if MODEL_1:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[1]})
  if MODEL_2:
    data_to_plot.append({'label': 'Model 2', 'data': res_global[2]})
  if MODEL_3:
    data_to_plot.append({'label': 'Model 3', 'data': res_global[3]})
  plot_data(
    data_to_plot,
    'Utilization',
    'Schedulable Tasksets',
    '')

def run_second ():
  global NO_MIG, MODEL_1, MODEL_2, MODEL_3
  res_global = [[], [], [], []]
  f = 1.25
  f_step = 0.25
  while f <= 3.75:
    print(f)
    total_utilizations = 0
    total_schedulable_utilizations = [0, 0, 0, 0]
    U = 3.2
    step = 0.028
    number_of_tests = 100
    while U <= 4.6:
      for n_task in range(number_of_tests):
        new_taskset = generate_taskset(24, 0.5, f, U)
        taskset_utilization = calc_total_utilization(new_taskset)
        total_utilizations += taskset_utilization
        if NO_MIG and verify_no_migration(copy.deepcopy(new_taskset)):
          for i in range(4):
            total_schedulable_utilizations[i] += taskset_utilization
        else:
          if MODEL_1 and verify_model_1(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[1] += taskset_utilization
          if MODEL_2 and verify_model_2(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[2] += taskset_utilization
          if MODEL_3 and verify_model_3(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[3] += taskset_utilization
      U += step
    for i in range(4):
      res_global[i].append([f, total_schedulable_utilizations[i] / total_utilizations])
    f += f_step
  data_to_plot = []
  if NO_MIG:
    data_to_plot.append({'label': 'No Migration', 'data': res_global[0]})
  if MODEL_1:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[1]})
  if MODEL_2:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[2]})
  if MODEL_3:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[3]})
  plot_data(
    data_to_plot,
    'Criticality Factor',
    'Weighted Schedulability',
    '')

def run_third ():
  global NO_MIG, MODEL_1, MODEL_2, MODEL_3
  res_global = [[], [], [], []]
  p = 0.1
  p_step = 0.2
  while p <= 0.9:
    print(p)
    total_utilizations = 0
    total_schedulable_utilizations = [0, 0, 0, 0]
    U = 3.2
    step = 0.028
    number_of_tests = 100
    while U <= 4.6:
      for n_task in range(number_of_tests):
        new_taskset = generate_taskset(24, p, 2, U)
        taskset_utilization = calc_total_utilization(new_taskset)
        total_utilizations += taskset_utilization
        if NO_MIG and verify_no_migration(copy.deepcopy(new_taskset)):
          for i in range(4):
            total_schedulable_utilizations[i] += taskset_utilization
        else:
          if MODEL_1 and verify_model_1(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[1] += taskset_utilization
          if MODEL_2 and verify_model_2(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[2] += taskset_utilization
          if MODEL_3 and verify_model_3(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[3] += taskset_utilization
      U += step
    for i in range(4):
      res_global[i].append([p, total_schedulable_utilizations[i] / total_utilizations])
    p += p_step
  data_to_plot = []
  if NO_MIG:
    data_to_plot.append({'label': 'No Migration', 'data': res_global[0]})
  if MODEL_1:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[1]})
  if MODEL_2:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[2]})
  if MODEL_3:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[3]})
  plot_data(
    data_to_plot,
    'Proportion of HI-crit tasks',
    'Weighted Schedulability',
    '')

def run_fourth ():
  global NO_MIG, MODEL_1, MODEL_2, MODEL_3
  res_global = [[], [], [], []]
  n = 32
  n_step = 16
  while n <= 144:
    print(n)
    total_utilizations = 0
    total_schedulable_utilizations = [0, 0, 0, 0]
    U = 3.2
    step = 0.028
    number_of_tests = 100
    while U <= 4.6:
      for n_task in range(number_of_tests):
        new_taskset = generate_taskset(n, 0.5, 2, U)
        taskset_utilization = calc_total_utilization(new_taskset)
        total_utilizations += taskset_utilization
        if NO_MIG and verify_no_migration(copy.deepcopy(new_taskset)):
          for i in range(4):
            total_schedulable_utilizations[i] += taskset_utilization
        else:
          if MODEL_1 and verify_model_1(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[1] += taskset_utilization
          if MODEL_2 and verify_model_2(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[2] += taskset_utilization
          if MODEL_3 and verify_model_3(copy.deepcopy(new_taskset)):
            total_schedulable_utilizations[3] += taskset_utilization
      U += step
    for i in range(4):
      res_global[i].append([n, total_schedulable_utilizations[i] / total_utilizations])
    n += n_step
  data_to_plot = []
  if NO_MIG:
    data_to_plot.append({'label': 'No Migration', 'data': res_global[0]})
  if MODEL_1:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[1]})
  if MODEL_2:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[2]})
  if MODEL_3:
    data_to_plot.append({'label': 'Model 1', 'data': res_global[3]})
  plot_data(
    data_to_plot,
    'Tasksets size',
    'Weighted Schedulability',
    '')