import os
import numpy as np
import matplotlib.pyplot as plt

class av_data():
    def __init__(self,name,av_velocity,av_torque):
        self.name = name
        self.av_torque = av_torque
        self.av_velocity = av_velocity
    
    def chop_small_torque(self, boundary):
        index = 0
        for element in self.av_torque:
            if element >= boundary:
                first_torque = element
                break
            index += 1
        for element in self.av_torque[index:]:
            if element < boundary:
                raise Exception('There is an element to the right of the minimum index that is smaller than the boundary.')
        self.av_torque = self.av_torque[index:]
        self.av_velocity = self.av_velocity[index:]
    
    def find_ext_reduction(self, reference):

        len_of_torque = len(self.av_torque)
        reference = reference[-len_of_torque:]
        
        difference = [1-self.av_torque[i]/reference[i] for i in range(len(self.av_torque))] 
        max_difference = max(difference)
        min_difference = min(difference)
        optimal_velocity = next((self.av_velocity[i] for i in range(len(self.av_velocity)) if 1-self.av_torque[i]/reference[i] == max_difference), None)
        min_velocity = next((self.av_velocity[i] for i in range(len(self.av_velocity)) if 1-self.av_torque[i]/reference[i] == min_difference), None)
        
        return max_difference, optimal_velocity, min_difference, min_velocity
        

def read_torque_csv(num_of_datapoints, name_of_reference, minimum_acceptable_torque):
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
                #if newline[0] > 10: #excluding velocities below 10/min
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
            element.chop_small_torque(minimum_acceptable_torque)
    
    for element in data:
        if element.name != reference.name:
            print(element.name, ', maximum reduction to reference: %f%%, at velocity: %.2f 1/min, minimum reduction to reference: %f%%, at velocity: %.2f 1/min'%(element.find_ext_reduction(reference.av_torque)[0]*100,element.find_ext_reduction(reference.av_torque)[1],element.find_ext_reduction(reference.av_torque)[2]*100,element.find_ext_reduction(reference.av_torque)[3]))



    
    
