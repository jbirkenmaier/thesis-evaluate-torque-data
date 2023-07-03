import os
import numpy as np
import matplotlib.pyplot as plt

class av_data():
    def __init__(self,name,av_velocity,av_torque):
        self.name = name
        self.av_velocity = av_velocity
        self.av_torque = av_torque

    def find_max_reduction(self, reference):
        difference = [1-self.av_torque[i]/reference[i] for i in range(len(reference))]  
        max_difference = max(difference)
        min_difference = min(difference)
        optimal_velocity = next((self.av_velocity[i] for i in range(len(self.av_velocity)) if 1-self.av_torque[i]/reference[i] == max_difference), None)
        
        return max_difference, optimal_velocity, min_difference
        

def read_torque_csv(num_of_datapoints, name_of_reference):
    csv_file_list = []
    data = []
    for element in os.listdir():
        file_object = os.path.isfile(element)
        if element.endswith('.csv'):
            csv_file_list.append(str(element))
    print(csv_file_list)
    for element in csv_file_list:
        velocity = []
        torque = []
        with open(element) as file:
            for line in file:
                newline = line.replace('\n','')
                newline = newline.split(',')
                newline = [float(element) for element in newline]
                if newline[0] > 10: #excluding velocities below 10/min
                    velocity.append(newline[0])
                    torque.append(newline[1])
            len_of_file=len(torque)
            print(len_of_file ,  element)
            avg_torque = [np.sum(torque[i:i+num_of_datapoints])/num_of_datapoints for i in range(0,len_of_file,num_of_datapoints)]
            avg_velocity = [np.sum(velocity[i:i+num_of_datapoints])/num_of_datapoints for i in range(0,len_of_file,num_of_datapoints)]
            data.append(av_data(element, avg_velocity, avg_torque))

    reference = next((element for element in data if element.name == name_of_reference),None)

    for element in data:
        if element.name != reference.name:
            print(element.name, ', maximum reduction to reference: %f%%, at velocity: %.2f 1/min'%(element.find_max_reduction(reference.av_torque)[0]*100,element.find_max_reduction(reference.av_torque)[1]))




    #print(reference.name)
    #print(reference.av_torque)

'''
def averaging_over(num_of_datapoints, data):
    avg_data = [np.sum(torque[i:i+num_of_datapoints])/num_of_datapoints for i in range(0,len_of_file-1,num_of_points)]
    for i in range(len(num_of_datapoints)):
'''        
    
    
