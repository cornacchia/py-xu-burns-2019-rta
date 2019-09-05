import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def plot_data (results, output):
  fig, ax = plt.subplots()
  for result in results:
    data = result['data']
    ax.plot([data[i][0] for i in range(len(data))], [data[i][1] for i in range(len(data))], label=result['label'])
  ax.set(xlabel="Utilization", ylabel="Scheduled Tasksets")
  ax.grid()
  #ax.xaxis.set_major_locator(ticker.MultipleLocator(500))
  #ax.yaxis.set_major_locator(ticker.MultipleLocator(500))
  plt.xticks()
  plt.legend()
  #plt.savefig(output)
  plt.show()