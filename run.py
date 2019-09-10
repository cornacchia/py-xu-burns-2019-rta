from taskset import generate_taskset, calc_total_utilization
from rta import verify_no_migration, verify_model_1
from plot import plot_data
import copy

def run_first ():
  res_no_migration_global = []
  res_model_1_global = []
  U = 3.2
  step = 0.028
  number_of_tests = 100
  while U <= 4.6:
    print(U)
    res_no_migration = [U, 0]
    res_model_1 = [U, 0]
    for n_task in range(number_of_tests):
      new_taskset = generate_taskset(24, 0.5, 2, U)
      if verify_no_migration(copy.deepcopy(new_taskset)):
        res_no_migration[1] += 1
      if verify_model_1(copy.deepcopy(new_taskset)):
        res_model_1[1] += 1
    res_no_migration[1] = res_no_migration[1] * 100 / number_of_tests
    res_model_1[1] = res_model_1[1] * 100 / number_of_tests
    res_no_migration_global.append(res_no_migration)
    res_model_1_global.append(res_model_1)
    U += step
  plot_data(
    [
      {'label': 'No Migration', 'data': res_no_migration_global},
      {'label': 'Model 1', 'data': res_model_1_global}
    ],
    'Utilization',
    'Schedulable Tasksets',
    '')

def run_second ():
  f_res_no_migration_global = []
  f_res_model_1 = []
  f = 1.25
  f_step = 0.25
  while f <= 3.75:
    print(f)
    total_utilizations = 0
    total_schedulable_utilizations_no_mig = 0
    total_schedulable_utilizations_model_1 = 0
    U = 3.2
    step = 0.028
    number_of_tests = 100
    while U <= 4.6:
      for n_task in range(number_of_tests):
        new_taskset = generate_taskset(24, 0.5, f, U)
        taskset_utilization = calc_total_utilization(new_taskset)
        total_utilizations += taskset_utilization
        if verify_no_migration(copy.deepcopy(new_taskset)):
          total_schedulable_utilizations_no_mig += taskset_utilization
        if verify_model_1(copy.deepcopy(new_taskset)):
          total_schedulable_utilizations_model_1 += taskset_utilization
      U += step
    f_res_no_migration_global.append([f, total_schedulable_utilizations_no_mig / total_utilizations])
    f_res_model_1.append([f, total_schedulable_utilizations_model_1 / total_utilizations])
    f += f_step
  plot_data(
    [
      {'label': 'No Migration', 'data': f_res_no_migration_global},
      {'label': 'Model 1', 'data': f_res_model_1}
      ],
    'Criticality Factor',
    'Weighted Schedulability',
    '')

def run_third ():
  p_res_no_migration_global = []
  p_res_model_1 = []
  p = 0.1
  p_step = 0.2
  while p <= 0.9:
    print(p)
    total_utilizations = 0
    total_schedulable_utilizations_no_mig = 0
    total_schedulable_utilizations_model_1 = 0
    U = 3.2
    step = 0.028
    number_of_tests = 100
    while U <= 4.6:
      for n_task in range(number_of_tests):
        new_taskset = generate_taskset(24, p, 2, U)
        taskset_utilization = calc_total_utilization(new_taskset)
        total_utilizations += taskset_utilization
        if verify_no_migration(copy.deepcopy(new_taskset)):
          total_schedulable_utilizations_no_mig += taskset_utilization
        if verify_model_1(copy.deepcopy(new_taskset)):
          total_schedulable_utilizations_model_1 += taskset_utilization
      U += step
    p_res_no_migration_global.append([p, total_schedulable_utilizations_no_mig / total_utilizations])
    p_res_model_1.append([p, total_schedulable_utilizations_model_1 / total_utilizations])
    p += p_step
  plot_data(
    [
      {'label': 'No Migration', 'data': p_res_no_migration_global},
      {'label': 'Model 1', 'data': p_res_model_1}
      ],
    'Proportion of HI-crit tasks',
    'Weighted Schedulability',
    '')

def run_fourth ():
  n_res_no_migration_global = []
  n = 32
  n_step = 16
  while n <= 144:
    print(n)
    total_utilizations = 0
    total_schedulable_utilizations = 0
    U = 3.2
    step = 0.028
    number_of_tests = 100
    while U <= 4.6:
      for n_task in range(number_of_tests):
        new_taskset = generate_taskset(n, 0.5, 2, U)
        taskset_utilization = calc_total_utilization(new_taskset)
        total_utilizations += taskset_utilization
        if verify_no_migration(new_taskset):
          total_schedulable_utilizations += taskset_utilization
      U += step
    n_res_no_migration_global.append([n, total_schedulable_utilizations / total_utilizations])
    n += n_step
  plot_data([{'label': 'No Migration', 'data': n_res_no_migration_global}], 'Tasksets size', 'Weighted Schedulability', '')

run_first()