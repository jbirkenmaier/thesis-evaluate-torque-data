import os
import math
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
        
        return max_difference, optimal_velocity, min_difference, min_velocity, difference

    def average_over_space(self, space_intervall, torque_reduction, velocity_steps = 5, maximum_velocity = 200):
        print(self.av_velocity[0])
        print(math.floor(self.av_velocity[0]/10)*10)
        num_of_intervalls = math.ceil((maximum_velocity + 1 - math.floor(self.av_velocity[0]/10)*10) / space_intervall) #+1 is important as it makes sure that if you land on a full number it will still be ceiled. If you land on 159, adding +1 does no harm, as it will not be ceiled. 
        print(len(self.av_torque))
        num_points_first_intervall=len(self.av_torque)-(num_of_intervalls-1)*space_intervall/velocity_steps#-1?????
        print(num_points_first_intervall)
        print(len(torque_reduction))
        intervalls = [space_intervall/velocity_steps for i in range(int(num_of_intervalls))]
        intervalls[0] = num_points_first_intervall
        print(intervalls)

        k=0
        av_torque_intervalled=[]
        for j in intervalls:
            print('-------', torque_reduction[k:k+int(j)])
            av_torque_intervalled.append(sum(torque_reduction[k:k+int(j)])/int(j))
            k+=int(j)
            
        print(torque_reduction)
            
        #    av_torque_intervalled = [np.sum(torque_reduction[i:i+int(j)])/int(j) for i in range(0, int(sum(intervalls)),int(j))]
        #print(av_torque_intervalled)
        return av_torque_intervalled

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

    for element in data:
        if element.name != reference.name:
            reduction_spaced_in_percent = element.average_over_space(50, element.find_ext_reduction(reference.av_torque)[4])
            reduction_spaced_in_percent = [element*100 for element in reduction_spaced_in_percent]
            print(reduction_spaced_in_percent)
            

    reduc =  data[0].find_ext_reduction(reference.av_torque)[4]

    print(reduc)
    print(len(reduc))
    
    num_points_first_intervall=len(data[0].av_torque)-(4-1)*(5-1)
    print(num_points_first_intervall)
    reduc = (sum(reduc[0:num_points_first_intervall-1]))/num_points_first_intervall
    print(reduc)
