from scipy.stats import lognorm
from scipy.stats import expon
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import random
import math
import statistics

#max number of calls handled
n = 41
#no_calls = 99
#values for random call generation 
maxValue = 3600
skewness = 0.5
average_no_calls=99
std_deviation = 27

#graph_x,graph_y=[],[]
# graph_y=[]
# graph_x2=[]
# graph_y2=[]


calls_list=[40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,148,152,156,160]
#calls_list=[40,44,48,52,56]
traffic_list=[10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40]
#generate random varibales for simulation
def create_random_variables(no_calls):

    #generate random start times
    random_call_start_times = np.random.random_sample(size = no_calls)
    random_call_start_times = random_call_start_times*3600


    #get random length of calls 
    #random_call_length2 = lognorm.rvs(s =skewness,loc=average_no_calls, size=no_calls)
    random_call_length2 = np.random.random_sample(size = no_calls)
    #print(random_call_length2)
    c = 0
    while c < len(random_call_length2):
        x = 1 - random_call_length2[c]
        random_call_length2[c] = math.log(x)/ -(1/900)
        c+=1
    
    #checks to make sure call length is ok
    if (len(random_call_length2) == 0):
        random_call_length2 = [0.1]
    for call in random_call_length2:
        if call < 0 or np.isnan(call):
            random_call_length2[call] = 0.1 

    #normalise data between 0-3600 seconds
    # np.seterr(all='raise')
    # try:
        # random_call_length2 = random_call_length2 - min(random_call_length2)
        # random_call_length2 = random_call_length2 / max(random_call_length2)
        # random_call_length2 = random_call_length2 * maxValue   
    # except FloatingPointError:
        # print("Invalid value caught and programme continues")

    #put random call lengths into a list parsed into ints
    # random_call_lengths_int = []
    # random_call_lengths_int2 = []
    # for value in random_call_length2:
        # if math.isnan(value):
            # random_call_lengths_int.append(900)
            # continue
        # random_call_lengths_int.append(int(value)) 

    # plt.hist(random_call_length2,30,density=True, color = 'red', alpha=0.1)
    # plt.xlabel("Duration in Seconds (s)")
    # plt.ylabel("Probability of occurance")
    # plt.show()

    #p = 0
    call_dict = {int(random_call_start_times[p]):int(random_call_length2[p]) for p in range(0,no_calls)}
    #assign call length to call start time
    #call_dict = {}
    # while p < no_calls:
        # call_dict.update({int(random_call_start_times[p]):random_call_lengths_int[p]})
        #p+=1
    #print(call_dict)
    #print(statistics.mean(random_call_length2))
    return call_dict


#carry out Monte Carlo Simulation
def simulate_calls(call_dict):
    time = 0
    simultaneous_calls=0
    dropped_calls={}
    skip_because_dropped=[]
    while time < maxValue:
        for call in call_dict.items():
            #If time = call start time, add it to simultaneous calls count, given there is room
            #otherwise drop call and add it to dropped_calls list
            if call[0] == time:
                if simultaneous_calls < n:
                    simultaneous_calls +=1
                else:
                    dropped_calls.update({call[0]:call[1]})
                    skip_because_dropped.append(call[0])
            #If call end time = time, take it off simultaneous call count
            #Check to make sure that call has not been dropped
            if (call[1] + call[0]) == time:
                if call[0] in skip_because_dropped:
                    continue
                simultaneous_calls -=1
        time +=1  

    #get params to calculate GOS manually
    #print("sum of call call durs %d"%sum(call_dict.values()))
    #print("no of calls: %d"%len(call_dict.values()))

    avg_call_duration = sum(call_dict.values())/len(call_dict.values())
    avg_offered_traffic = (avg_call_duration/maxValue)*len(call_dict.values())
    avg_GOS_from_dropped = 100*len(dropped_calls)/len(call_dict)

    return(avg_offered_traffic,avg_GOS_from_dropped)


def calculate_GOS_erlangb(bottom_range,top_range):
    graph_x2 = []
    graph_y2 = []
    all_data= []
    iterator = bottom_range
    while iterator <= top_range:
        Ao = iterator
        i,n_factorial = 1,1
        #n_factorial = 1
        factorial_list=[]
        numerator = 0
        #calculate factorial
        while i <= n:
            n_factorial= n_factorial * i
            factorial_list.append(n_factorial)
            i +=1
        #calculate numerator
        numerator = (Ao**n)/factorial_list[n-1]
        denominator=0
        j = 1
        #calculate denominator
        while j <= len(factorial_list):
            denominator +=(Ao**j)/factorial_list[j-1]
            j+=1
        denominator +=1
        #calculate GOS
        E1 = numerator/denominator
        iterator +=1
        all_data.append([Ao,E1*100])
        graph_x2.append(Ao)
        graph_y2.append(E1*100)
        
    return graph_x2,graph_y2


if __name__ == "__main__":
    print("Please wait a moment while the programme executes...")
    graph_x,graph_y,GOS_stdev=[],[],[]
  
    for no_calls in calls_list:
        k=0
        Ao_list=[]
        call_GOS = []
        while k < 100:
            call_dictionary = create_random_variables(no_calls)
            offered_traffic,GOS =simulate_calls(call_dictionary)
            Ao_list.append(offered_traffic)
            call_GOS.append(GOS)
            k+=1
        graph_x.append(statistics.mean(Ao_list))
        graph_y.append(statistics.mean(call_GOS))
        GOS_stdev.append(statistics.stdev(call_GOS))
    
    x,y = calculate_GOS_erlangb(10,40)

    plt.plot(x,y,label="Erlang B Formula")

    plt.plot(graph_x,graph_y,label="Monte Carlo Simulation")
    plus_stdev = [graph_y[l]+ 2*GOS_stdev[l] for l in range (0,len(GOS_stdev))]
    minus_stdev = [graph_y[l]- 2*GOS_stdev[l] if graph_y[l]- 2*GOS_stdev[l] >=0 else 0 for l in range (0,len(GOS_stdev))]
    plt.plot(graph_x,plus_stdev,label="Simulation +2 stdev")
    plt.plot(graph_x,minus_stdev,label="Simulation -2 stdev")

    plt.xlabel("Ao")
    plt.ylabel("GOS")
    plt.title("Erlang B formula Vs Simulation with Lognormal Distribution of Call Lengths")
    plt.title("Erlang B formula Vs Simulation with Decaing Exponential Distribution of Call Lengths")
    plt.legend(loc='upper left')
    plt.show()
    