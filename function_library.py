import os
import math
import numpy as np
import matplotlib.pyplot as plt

class av_data():
    def __init__(self,name,av_velocity,av_torque):
        self.name = name
        self.av_torque = av_torque
        self.av_velocity = av_velocity
        self.intervall_denumerator = []
    
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
        num_of_intervalls = math.ceil((maximum_velocity + 1 - math.floor(self.av_velocity[0]/10)*10) / space_intervall) #+1 is important as it makes sure that if you land on a full number it will still be ceiled. If you land on 159, adding +1 does no harm, as it will not be ceiled.
        self.intervall_denumerator = [i  for i in range(int(maximum_velocity/space_intervall))]
        num_points_first_intervall=len(self.av_torque)-(num_of_intervalls-1)*space_intervall/velocity_steps
        intervalls = [space_intervall/velocity_steps for i in range(int(num_of_intervalls))]
        intervalls[0] = num_points_first_intervall
        chopped_intervalls = len(self.intervall_denumerator)-len(intervalls)
        self.intervall_denumerator = self.intervall_denumerator[chopped_intervalls:]
        self.intervall_denumerator = ['(%.f - %.f)/min'%(element*space_intervall, (element+1)*space_intervall) for element in self.intervall_denumerator]
        k=0
        av_torque_intervalled=[]
        for j in intervalls:
            av_torque_intervalled.append(sum(torque_reduction[k:k+int(j)])/int(j))
            k+=int(j)            
        return av_torque_intervalled

def read_torque_csv(num_of_datapoints, name_of_reference, minimum_acceptable_torque, intervall_range,results_filename_max_reduction,results_filename_intervalled_reduction):
    try: 
        os.remove(results_filename_max_reduction)
        os.remove(results_filename_intervalled_reduction)
    except:
        pass
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
                try:
                    newline = line.replace('\n','')
                    newline = newline.split(',')
                    newline = [float(content) for content in newline]
                    velocity.append(newline[0])
                    torque.append(newline[1])
                except:
                    continue
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
            max_reduction_torque = element.find_ext_reduction(reference.av_torque)[0]*100
            max_reduction_velocity = element.find_ext_reduction(reference.av_torque)[1]
            min_reduction_torque = element.find_ext_reduction(reference.av_torque)[2]*100
            min_reduction_velocity = element.find_ext_reduction(reference.av_torque)[3]
            
            print(element.name, ', maximum reduction to reference: %f%%, at velocity: %.2f 1/min, minimum reduction to reference: %f%%, at velocity: %.2f 1/min'%(max_reduction_torque,max_reduction_velocity,min_reduction_torque,min_reduction_velocity))  

            with open(results_filename_max_reduction,'a') as file:
                file.write(str(element.name)[:-18].replace('_',' ')+','+ str(max_reduction_torque)+','+ str(max_reduction_velocity)+','+str(min_reduction_torque)+','+str(min_reduction_velocity)+'\n')

    legend_names = [element.name for element in data]
    fig, ax = plt.subplots()
    
    ax.set_prop_cycle(color=[
    '#1f77b4',  # Dark blue
    'black',    # Black
    '#d62728',  # Dark red
    '#9467bd',  # Dark purple
    '#8c564b',  # Brown
    '#e377c2',  # Pink
    '#7f7f7f',  # Gray
    '#bcbd22',  # Olive
    '#17becf',  # Teal
    '#1b9e77',  # Light green
    '#8B8000',  # Dark yellow
    '#ff7f0e',  # Dark orange
    '#66c2a5',  # Seafoam green
    '#ff1493',  # Deep pink
    ])
    
    for element in data:
        if element.name != reference.name:
            reduction_spaced_in_percent = element.average_over_space(intervall_range, element.find_ext_reduction(reference.av_torque)[4])
            reduction_spaced_in_percent = [element*100 for element in reduction_spaced_in_percent]
            plt.plot(element.intervall_denumerator,reduction_spaced_in_percent, '.')
            reduction_spaced_in_percent = [str(element*100)for element in reduction_spaced_in_percent]
            print(element.name,'average reduction in intervalls of %i 1/min: '%intervall_range, reduction_spaced_in_percent)
            print(element.intervall_denumerator)
            with open(results_filename_intervalled_reduction,'a') as file:
                file.write(str(element.name)[:-18].replace('_',' ')+','+ ','.join(reduction_spaced_in_percent)+'\n')

    plt.legend(legend_names, bbox_to_anchor=(1.00,1.0), loc='best')
    plt.tight_layout()
    plt.show()
