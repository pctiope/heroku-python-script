import numpy as np

def update_average(array):
    ave = []
    
    for i in range(len(array[0])):
        listy = [float(array[j][i]) for j in range(len(array))]
        ave.append(np.mean(listy))
    return ave