
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
bottom_range = 10
top_range = 40

numValues = 1000
maxValue = 3600
skewness = 0.5

average_no_calls=99
std_deviation = 55

def create_random_variables():
    no_calls = int(random.normalvariate(average_no_calls,std_deviation))
    if no_calls <= 0:
        no_calls = 67

    #get random length of calls 
    random_call_length2 = lognorm.rvs(s =skewness,loc=average_no_calls, size=no_calls)

    if (len(random_call_length2) == 0):
        random_call_length2 = [0.1,0.2,0.3]
    for call in random_call_length2:
        if call < 0 or np.isnan(call):
            random_call_length2[call] = 0.1 

    np.seterr(all='raise')
    try:
        random_call_length2 = random_call_length2 - min(random_call_length2)
        random_call_length2 = random_call_length2 / max(random_call_length2)
        random_call_length2 = random_call_length2 * maxValue   
    except FloatingPointError:
        print("Invalid value caught and programme continues")

    # plt.hist(random_call_length2,30,density=True, color = 'red', alpha=0.1)
    # plt.xlabel("Duration in Seconds (s)")
    # plt.ylabel("Probability of occurance")
    # plt.show()

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
    return call_dict,time_between_calls

call_dict2 = {
    2:12,
    5:5,
    8:20,
    11: 10
}
def simulate_calls(call_dict,time_interval):
    time = 0
    simultaneous_calls=0
    dropped_calls={}
    skip_because_dropped=[]
    queue_stack=[]
    queued_calls = {}
    completed_queued_calls = {}

    # call_dict_times = call_dict.items()
    # print(call_dict_times)
    # call_interval = call_dict_times[1][0] - call_dict_times[0][0]
    # # print(call_interval)
    #time_interval = 0
    while time < 3600:

        for q0 in queued_calls.items():
            # print("got in q")
            # print(q0[0])
            # print(q0[1])
            if q0[0] == time:
                if simultaneous_calls < n:
                    #print("adding one from q")
                    simultaneous_calls +=1
                #print((q0[0] + q0[1]))
            if (q0[1] + q0[0]) == time:
                #print("taken a q off because done")
                simultaneous_calls -=1
                completed_queued_calls.update({q0[0]-900:q0[1]-900})
                
        for call in call_dict.items():
            if call[0] == time:
                if simultaneous_calls < n:
                    #print("adding one to the pack")
                    simultaneous_calls +=1
                else:
                    queued_calls.update({call[0]+900:call[1]+900})
                    dropped_calls.update({call[0]:call[1]})
                    skip_because_dropped.append(call[0])
            if (call[1] + call[0]) == time:
                if call[0] in skip_because_dropped:
                    continue
                simultaneous_calls -=1
            #print(len(queued_calls.items()))

        

        #print("number of calls at %d seconds: %d"%(time,simultaneous_calls))
        time +=1  
    end_q = {}
    for d1 in queued_calls.items():
        #print(d1)
        #print(completed_queued_calls)
        #print(completed_queued_calls[0])
        check = (d1[0]-900,d1[1]-900)
        #print(check)
        if check not in completed_queued_calls.items():
                end_q.update({d1[0]-900:d1[1]-900})
    # print("end_q")
    # print(end_q)
    # print("length")
    # print(len(end_q))
    # print("completed")
    # print(completed_queued_calls)
    # print("dropped")
    # print(dropped_calls)

    avg_call_duration = sum(call_dict.values())/len(call_dict.values())
    avg_offered_traffic = (avg_call_duration/maxValue)*len(call_dict.values())

    #print(avg_call_duration)
    avg_GOS = calculate_GOS(avg_offered_traffic)
    return(avg_call_duration,len(call_dict),avg_offered_traffic,avg_GOS,len(end_q))

def calculate_GOS_erlangb():
    all_data= []
    iterator = bottom_range
    while iterator <= top_range:
        Ao = iterator
        i = 1
        n_factorial = 1
        factorial_list=[]
        numerator = 0
        while i <= n:
            n_factorial= n_factorial * i
            factorial_list.append(n_factorial)
            i +=1
        numerator = (Ao**n)/factorial_list[n-1]
        denominator=0
        j = 1
        while j <= len(factorial_list):
            denominator +=(Ao**j)/factorial_list[j-1]
            j+=1
        denominator +=1
        #print(denominator)
        E1 = numerator/denominator
        iterator +=1
        all_data.append([Ao,E1*100])
    return all_data

def calculate_GOS(Ao):
    i = 1
    n_factorial = 1
    factorial_list=[]
    numerator = 0
    while i <= n:
        n_factorial= n_factorial * i
        factorial_list.append(n_factorial)
        i +=1
    try:
        a_add_on = n/(n-Ao)
    except ZeroDivisionError:
        a_add_on = 0 
    numerator = ((Ao**n)/factorial_list[n-1]) * a_add_on
    denominator=0
    j = 1
    while j <= len(factorial_list):
        denominator +=(Ao**j)/factorial_list[j-1]
        j+=1
    denominator +=1
    denominator += ((Ao ** n)/factorial_list[n-1] * a_add_on)
    E1 = numerator/denominator
    return (E1*100)

def calculate_ErlangC(Ao):
    i = 1
    n_factorial = 1
    factorial_list=[]
    numerator = 0
    while i <= n:
        n_factorial= n_factorial * i
        factorial_list.append(n_factorial)
        i +=1
    try:
        a_add_on = n/(n-Ao)
    except ZeroDivisionError:
        a_add_on = 0 
    numerator = ((Ao**n)/factorial_list[n-1]) * a_add_on
    denominator=0
    j = 1
    while j <= len(factorial_list):
        denominator +=(Ao**j)/factorial_list[j-1]
        j+=1
    denominator +=1
    denominator += ((Ao ** n)/factorial_list[n-1] * a_add_on)
    E1 = numerator/denominator
    return (E1*100)

if __name__ == "__main__":
    simulation_list = []

    print("Please wait a moment while the programme executes...")
    k=0
    while k < 1:
        call_dictionary,time_interval = create_random_variables()
        call_dur,calls,offered_traffic,GOS,dropped_calls =simulate_calls(call_dictionary,time_interval)
        simulation_list.append([call_dur,calls,offered_traffic,GOS,dropped_calls])
        k+=1
    
    # call_dictionary = create_random_variables()
    # call_dur,calls,offered_traffic,GOS,dropped_calls =simulate_calls(call_dictionary)
    print("\nResults from Monte deCarlo simulation. Offered traffic varied with random number of calls and varied call length.\nConstant channels = 41")
    results_df = pd.DataFrame.from_records(simulation_list, columns=['Avg Call Duration',
                                                           'Avg No Calls',
                                                           'Avg Offered Traffic',
                                                           'Avg GOS',
                                                           'Avg No Dropped Calls'])
    print(results_df.describe())
    results_df.describe().style.format('{:,}')
    
    erlangB_list = []
    erlangB_list = calculate_GOS_erlangb()
    resultsB = pd.DataFrame.from_records(erlangB_list, columns=[
                                                           'Avg Offered Traffic',
                                                           'Avg GOS'])
    print("\n\nResults from Erlang B formula. Offered traffic varied not taking into account individual call length or number of calls.\nConstant channels = 41")
    print(resultsB.describe())
    
    