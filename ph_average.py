import numpy as np

def update_average(array):
    ave = []
    for i in range(200):
        listy = [array[j][i] for j in range(len(array))]
        ave.append(np.mean(listy))
    return ave