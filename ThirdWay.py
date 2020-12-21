from scipy.stats import lognorm
from scipy.stats import expon
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import random
import math

#max number of calls handled
n = 41
no_calls = 99
#values for random call generation 
maxValue = 3600
skewness = 0.55
average_no_calls=99
std_deviation = 27

graph_x=[]
graph_y=[]
graph_x2=[]
graph_y2=[]


#generate random varibales for simulation
def create_random_variables():

    #generate random start times
    random_call_start_times = np.random.random_sample(size = no_calls)
    random_call_start_times =  random_call_start_times*3600
    c = 0
    while c < no_calls:
        random_call_start_times[c]=int(random_call_start_times[c])
        c +=1

    #get random length of calls 
    random_call_length2 = lognorm.rvs(s =skewness,loc=average_no_calls, size=no_calls)
    #random_call_length2 = np.random.random_sample(size = no_calls)
    # c = 0
    # while c < len(random_call_length2):
    #     x = 1 - random_call_length2[c]
    #     random_call_length2[c] = math.log(x)/ -(1/900)
    #     c+=1
    
    #checks to make sure call length is ok
    if (len(random_call_length2) == 0):
        random_call_length2 = [0.1]
    for call in random_call_length2:
        if call < 0 or np.isnan(call):
            random_call_length2[call] = 0.1 

    #normalise data between 0-3600 seconds
    np.seterr(all='raise')
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

    # plt.hist(random_call_length2,30,density=True, color = 'red', alpha=0.1)
    # plt.xlabel("Duration in Seconds (s)")
    # plt.ylabel("Probability of occurance")
    # plt.show()

    p = 0
    #time_between_calls = int(maxValue/no_calls)
    #time=0
    call_dict = {}
    #avg =0
    #assign call length to call start time
    while p < no_calls:
        #time += time_between_calls
        call_dict.update({random_call_start_times[p]:random_call_lengths_int[p]})
        #avg += (99*random_call_lengths_int[p]/3600)
        p+=1
    # print(avg/99)
    # print(call_dict)
    return call_dict


#carry out Monte Carlo Simulation
def simulate_calls(call_dict):
    # global graph_x
    # global graph_y
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
    avg_call_duration = sum(call_dict.values())/len(call_dict.values())
    avg_offered_traffic = (avg_call_duration/maxValue)*len(call_dict.values())
    avg_GOS_from_dropped = 100*len(dropped_calls)/len(call_dict)

    #add Ao and GOS to the list for graphing
    # graph_x.append(avg_offered_traffic)
    # graph_y.append(avg_GOS_from_dropped)

    return(avg_call_duration,len(call_dict),avg_offered_traffic,avg_GOS_from_dropped,len(dropped_calls))


def calculate_GOS_erlangb(bottom_range,top_range):
    global graph_x2
    global graph_y2
    all_data= []
    iterator = bottom_range
    while iterator <= top_range:
        Ao = iterator
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
        iterator +=1
        all_data.append([Ao,E1*100])
        graph_x2.append(Ao)
        graph_y2.append(E1*100)
        
    return all_data


if __name__ == "__main__":
    simulation_list = []
    print("Please wait a moment while the programme executes...")
 
    k=0
    while k < 10:
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
    graph_x.append(results_df['Avg Offered Traffic'].mean())
    graph_y.append(results_df['Avg GOS'].mean())
    print(graph_x)
    print(graph_y)
    print(results_df.describe())
    results_df.describe().style.format('{:,}')

    #xs, ys = zip(*sorted(zip(graph_x, graph_y)))

    calculate_GOS_erlangb(results_df['Avg Offered Traffic'].min(),results_df['Avg Offered Traffic'].max())
    plt.plot(graph_x2,graph_y2)
    plt.plot(graph_x,graph_y)
    plt.xlabel("Ao")
    plt.ylabel("GOS")
    plt.title("Erlang B formula Vs Simulation with Decaying Exponential")
    plt.show()
    