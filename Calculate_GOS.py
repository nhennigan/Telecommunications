
from scipy.stats import skewnorm
from scipy.stats import lognorm
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import random
import math
import warnings

#offered traffic
Ao = 25
#max number of calls handled
n = 41

#values for random call generation
maxValue = 3600
skewness = 0.5
average_no_calls=99
std_deviation = 27

#generate random varibales for simulation
def create_random_variables():
    #generate random # of calls from normal distribution
    no_calls = int(random.normalvariate(average_no_calls,std_deviation))
    if no_calls <= 0:
        no_calls = 67

    #get random length of calls 
    random_call_length2 = lognorm.rvs(s =skewness,loc=average_no_calls, size=no_calls)

    #checks to make sure call lenght is ok
    if (len(random_call_length2) == 0):
        random_call_length2 = [0.1,0.2,0.3]
    for call in random_call_length2:
        if call < 0 or np.isnan(call):
            random_call_length2[call] = 0.1 

    np.seterr(all='raise')
    #normalise data between 0-3600 seconds
    try:
        random_call_length2 = random_call_length2 - min(random_call_length2)
        random_call_length2 = random_call_length2 / max(random_call_length2)
        random_call_length2 = random_call_length2 * maxValue   
    except FloatingPointError:
        print("Invalid value caught and programme continues")

    #put random call lengths into a list parsed into ints
    random_call_lengths_int = []
    for value in random_call_length2:
        if math.isnan(value):
            random_call_lengths_int.append(900)
            continue
        random_call_lengths_int.append(int(value)) 
        #maybe put in a check that it doesn't go over 3600 in length

    p = 0
    time_between_calls = int(maxValue/no_calls)
    time=0
    call_dict = {}

    #assign call length to call start time
    while p < no_calls:
        time += time_between_calls

        call_dict.update({time:random_call_lengths_int[p]})
        p+=1
    return call_dict

#carry out Monte Carlo Simulation
def simulate_calls(call_dict):
    time = 0
    simultaneous_calls=0
    dropped_calls={}
    skip_because_dropped=[]
    while time < maxValue:
        for call in call_dict.items():
            #If time = call start time, add it to simultaneous calls count
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

    #get params and calculate Erlang B GOS
    avg_call_duration = sum(call_dict.values())/len(call_dict.values())
    avg_offered_traffic = (avg_call_duration/maxValue)*len(call_dict.values())
    avg_GOS = calculate_erlangB(avg_offered_traffic)

    return(avg_call_duration,len(call_dict),avg_offered_traffic,avg_GOS,len(dropped_calls))

def calculate_erlangB(Ao):
    i = 1
    n_factorial = 1
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
    return (E1*100)

if __name__ == "__main__":
    simulation_list = []

    print("Please wait a moment while the programme executes...")
    
    k=0
    while k < 1000:
        call_dictionary = create_random_variables()
        call_dur,calls,offered_traffic,GOS,dropped_calls =simulate_calls(call_dictionary)
        simulation_list.append([call_dur,calls,offered_traffic,GOS,dropped_calls])
        k+=1
    
    print("\nResults from Monte deCarlo simulation with Erlang B.\nOffered traffic varied with random number of calls and varied call length.\nConstant channels = 41")
    results_df = pd.DataFrame.from_records(simulation_list, columns=['Avg Call Duration',
                                                           'Avg No Calls',
                                                           'Avg Offered Traffic',
                                                           'Avg GOS',
                                                           'Avg No Dropped Calls'])
    print(results_df.describe())
    results_df.describe().style.format('{:,}')
 
    
    