from taskset import generate_taskset
from rta import verify_no_migration
from plot import plot_data

def run ():
  res_no_migration_global = []
  U = 3.2
  step = 0.028
  number_of_tests = 100
  while U < 4.6:
    print(U)
    res_no_migration = [U, 0]
    for n_task in range(number_of_tests):
      new_taskset = generate_taskset(24, 0.5, 2, U)
      if verify_no_migration(new_taskset):
        res_no_migration[1] += 1
    res_no_migration[1] = res_no_migration[1] * 100 / number_of_tests
    res_no_migration_global.append(res_no_migration)
    U += step
  plot_data([{'label': 'No Migration', 'data': res_no_migration_global}], "")

run()