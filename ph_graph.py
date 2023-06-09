import csv
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from os.path import join
from ph_average import update_average

dataset_path = "./results"
bicycle_csv = []
pedestrian_csv = []
final_csv = []

def plot_all():
    for f in listdir(dataset_path):
        for g in listdir(join(dataset_path,f)):
            if g == 'bicycle':
                for h in listdir(join(dataset_path,f,g)):
                    if h == '0':
                        bicycle_csv.extend(
                            join(dataset_path, f, g, h, i)
                            for i in listdir(join(dataset_path, f, g, h))
                            if i == 'data.csv'
                        )
            if g == 'pedestrian':
                for h in listdir(join(dataset_path,f,g)):
                    if h == '0':
                        pedestrian_csv.extend(
                            join(dataset_path, f, g, h, i)
                            for i in listdir(join(dataset_path, f, g, h))
                            if i == 'data.csv'
                        )
            if g == 'final':
                for h in listdir(join(dataset_path,f,g)):
                    if h == '0':
                        final_csv.extend(
                            join(dataset_path, f, g, h, i)
                            for i in listdir(join(dataset_path, f, g, h))
                            if i == 'data.csv'
                        )

    bicycle_cnt = len(bicycle_csv)
    pedestrian_cnt = len(pedestrian_csv)
    final_cnt = len(final_csv)

    bicycle_ave_threshold_exposure = []
    bicycle_ave_time_exposure = []
    bicycle_ave_time_sum = []
    pedestrian_ave_threshold_exposure = []
    pedestrian_ave_time_exposure = []
    pedestrian_ave_time_sum = []
    final_threshold_exposure = []
    final_time_exposure = []
    final_time_sum = []

    total_bicycle_ave_threshold_exposure = []
    total_bicycle_ave_time_exposure = []
    total_bicycle_ave_time_sum = []
    total_pedestrian_ave_threshold_exposure = []
    total_pedestrian_ave_time_exposure = []
    total_pedestrian_ave_time_sum = []
    total_final_threshold_exposure = []
    total_final_time_exposure = []
    total_final_time_sum = []

    for bicycle_filename in bicycle_csv:
        with open(bicycle_filename, mode='r') as bicycle_file:
            csvFile = csv.reader(bicycle_file)
            for lines in csvFile:
                bicycle_ave_threshold_exposure.append(lines[0])
                bicycle_ave_time_exposure.append(lines[1])
                bicycle_ave_time_sum.append(lines[2])
            bicycle_ave_threshold_exposure.pop(0)
            bicycle_ave_time_exposure.pop(0)
            bicycle_ave_time_sum.pop(0)
        total_bicycle_ave_threshold_exposure.append(bicycle_ave_threshold_exposure)
        total_bicycle_ave_time_exposure.append(bicycle_ave_time_exposure)
        total_bicycle_ave_time_sum.append(bicycle_ave_time_sum)
        bicycle_ave_threshold_exposure = []
        bicycle_ave_time_exposure = []
        bicycle_ave_time_sum = []

    for pedestrian_filename in pedestrian_csv:
        with open(pedestrian_filename, mode='r') as pedestrian_file:
            csvFile = csv.reader(pedestrian_file)
            for lines in csvFile:
                pedestrian_ave_threshold_exposure.append(lines[0])
                pedestrian_ave_time_exposure.append(lines[1])
                pedestrian_ave_time_sum.append(lines[2])
            pedestrian_ave_threshold_exposure.pop(0)
            pedestrian_ave_time_exposure.pop(0)
            pedestrian_ave_time_sum.pop(0)
        total_pedestrian_ave_threshold_exposure.append(pedestrian_ave_threshold_exposure)
        total_pedestrian_ave_time_exposure.append(pedestrian_ave_time_exposure)
        total_pedestrian_ave_time_sum.append(pedestrian_ave_time_sum)
        pedestrian_ave_threshold_exposure = []
        pedestrian_ave_time_exposure = []
        pedestrian_ave_time_sum = []

    for final_filename in final_csv:
        with open(final_filename, mode='r') as final_file:
            csvFile = csv.reader(final_file)
            for lines in csvFile:
                final_threshold_exposure.append(lines[6])
                final_time_exposure.append(lines[7])
                final_time_sum.append(lines[8])
            final_threshold_exposure.pop(0)
            final_time_exposure.pop(0)
            final_time_sum.pop(0)
        total_final_threshold_exposure.append(final_threshold_exposure)
        total_final_time_exposure.append(final_time_exposure)
        total_final_time_sum.append(final_time_sum)
        final_threshold_exposure = []
        final_time_exposure = []
        final_time_sum = []
            
    # print(total_bicycle_ave_threshold_exposure)
    mean_bicycle_ave_threshold_exposure = update_average(total_bicycle_ave_threshold_exposure)
    mean_bicycle_ave_time_exposure = update_average(total_bicycle_ave_time_exposure)
    mean_bicycle_ave_time_sum = update_average(total_bicycle_ave_time_sum)
    mean_pedestrian_ave_threshold_exposure = update_average(total_pedestrian_ave_threshold_exposure)
    mean_pedestrian_ave_time_exposure = update_average(total_pedestrian_ave_time_exposure)
    mean_pedestrian_ave_time_sum = update_average(total_pedestrian_ave_time_sum)
    mean_final_threshold_exposure = update_average(total_final_threshold_exposure)
    mean_final_time_exposure = update_average(total_final_time_exposure)
    mean_final_time_sum = update_average(total_final_time_sum)

    x = np.linspace(0, 1, num=200)

    bicycle_ave_time_exposure_y = np.mean(mean_bicycle_ave_time_exposure, axis=0)
    bicycle_ave_threshold_exposure_y = np.mean(mean_bicycle_ave_threshold_exposure, axis=0)
    bicycle_ave_time_y = np.mean(mean_bicycle_ave_time_sum, axis=0)

    plt.plot(x, mean_bicycle_ave_time_exposure, linewidth=1, label='time vs exposure')
    plt.axhline(y=bicycle_ave_time_exposure_y, color='r', linestyle='--', label='bicycle ave relative exposure')
    plt.xlabel('bicycle relative time')
    plt.ylabel('bicycle relative average exposure')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()
    plt.plot(x, mean_bicycle_ave_threshold_exposure, linewidth=1, label='threshold vs exposure')
    plt.axhline(y=bicycle_ave_threshold_exposure_y, color='r', linestyle='--', label='bicycle ave relative exposure')
    plt.xlabel('bicycle relative threshold')
    plt.ylabel('bicycle relative average exposure')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()
    plt.plot(x, mean_bicycle_ave_time_sum, linewidth=1, label='threshold vs time')
    plt.axhline(y=bicycle_ave_time_y, color='r', linestyle='--', label='bicycle ave time exposure')
    plt.xlabel('bicycle relative threshold')
    plt.ylabel('bicycle relative time')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()

    pedestrian_ave_time_exposure_y = np.mean(mean_pedestrian_ave_time_exposure, axis=0)
    pedestrian_ave_threshold_exposure_y = np.mean(mean_pedestrian_ave_threshold_exposure, axis=0)
    pedestrian_ave_time_y = np.mean(mean_pedestrian_ave_time_sum, axis=0)

    plt.plot(x, mean_pedestrian_ave_time_exposure, linewidth=1, label='time vs exposure')
    plt.axhline(y=pedestrian_ave_time_exposure_y, color='r', linestyle='--', label='pedestrian ave relative exposure')
    plt.xlabel('pedestrian relative time')
    plt.ylabel('pedestrian relative average exposure')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()
    plt.plot(x, mean_pedestrian_ave_threshold_exposure, linewidth=1, label='threshold vs exposure')
    plt.axhline(y=pedestrian_ave_threshold_exposure_y, color='r', linestyle='--', label='pedestrian ave relative exposure')
    plt.xlabel('pedestrian relative threshold')
    plt.ylabel('pedestrian relative average exposure')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()
    plt.plot(x, mean_pedestrian_ave_time_sum, linewidth=1, label='threshold vs time')
    plt.axhline(y=pedestrian_ave_time_y, color='r', linestyle='--', label='pedestrian ave time exposure')
    plt.xlabel('pedestrian relative threshold')
    plt.ylabel('pedestrian relative time')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()

    final_time_exposure_y = np.mean(mean_final_time_exposure, axis=0)
    final_threshold_exposure_y = np.mean(mean_final_threshold_exposure, axis=0)
    final_time_y = np.mean(mean_final_time_sum, axis=0)

    plt.plot(x, mean_final_time_exposure, linewidth=1, label='time vs exposure')
    plt.axhline(y=final_time_exposure_y, color='r', linestyle='--', label='final ave relative exposure')
    plt.xlabel('final relative time')
    plt.ylabel('final relative average exposure')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()
    plt.plot(x, mean_final_threshold_exposure, linewidth=1, label='threshold vs exposure')
    plt.axhline(y=final_threshold_exposure_y, color='r', linestyle='--', label='final ave relative exposure')
    plt.xlabel('final relative threshold')
    plt.ylabel('final relative average exposure')
    plt.legend(loc="upper right")
    plt.figure()
    # plt.show()
    plt.plot(x, mean_final_time_sum, linewidth=1, label='threshold vs time')
    plt.axhline(y=final_time_y, color='r', linestyle='--', label='final ave time exposure')
    plt.xlabel('final relative threshold')
    plt.ylabel('final relative time')
    plt.legend(loc="upper right")
    # plt.figure()
    plt.show()
    
plot_all()