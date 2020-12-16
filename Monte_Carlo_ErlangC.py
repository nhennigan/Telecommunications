
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
n = 2
bottom_range = 10
top_range = 40

numValues = 1000
maxValue = 3600
skewness = 0.5

average_no_calls=99
std_deviation = 25

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
    11:10
}
def simulate_calls(call_dict,time_interval):
    time = 0
    simultaneous_calls=0
    dropped_calls={}
    skip_because_dropped=[]
    queued_calls = {}
    completed_queued_calls = {}
    requeued = {}
    call_index=0
    while time < 50:
        
        sim_before_q = simulate_calls
        #flag = false
        q = 0
        print(len(queued_calls))
        while q < len(queued_calls):
        #for q0 in queued_calls.items():
            #print("q")
            #print(q)
            print("queued_calls[q]")
            print(queued_calls[q])
            if queued_calls[q][0] == time:  
                if simultaneous_calls < n:
                    print("added one from q")
                    simultaneous_calls +=1
                    completed_queued_calls.update({queued_calls[q][0]:queued_calls[q][1]})
                else:
                    requeued.update({queued_calls[q][0]:queued_calls[q][1]})
                    print("requeued")
                    print(requeued)
                    #flag = true
                    # start_time = q0[1][0]
                    # dur = q0[1][1]
                    #queued_calls[q0].update(start_time= q0[0]+1 ,dur= q0[1]+1)
                    queued_calls[q][0]+=1
                    #queued_calls[q][1]+=1
                    #queued_calls[q0] = (q0[1][0]+1,q0[1][1]+1)
                    #print(queued_calls[q])
            
                    #queued_calls[q][1][1] = (q0[1][1]+1)
                    # queued_calls[q0[0]+1] = queued_calls[q0[0]]
            if (queued_calls[q][0] + queued_calls[q][1]) == time:
                if queued_calls[q][0] in requeued:
                    print("skipping becuase not really on queue yet")
                    continue
                print("q minus")
                simultaneous_calls -=1
            q+=1
        #if len(queued_calls) != 0 and sim_before_q < 
        print(queued_calls)
        print(completed_queued_calls)

        for call in call_dict.items():
            if call[0] == time:
                if simultaneous_calls < n:
                    simultaneous_calls +=1
                else:
                    queued_calls[call_index] = list()
                    queued_calls[call_index].extend((call[0]+1,call[1]+1))
                    #print(queued_calls)
                    #print(queued_calls[call_index][0])
                    call_index +=1
                    #dropped_calls.update({call[0]:call[1]})
                    skip_because_dropped.append(call[0])
            if (call[1] + call[0]) == time:
                if call[0] in skip_because_dropped:
                    continue
                simultaneous_calls -=1
        print("number of calls at %d seconds: %d"%(time,simultaneous_calls))
        time +=1  
        
    end_q_length = len(queued_calls) - len(completed_queued_calls)
    

    # for d1 in queued_calls.items():
    #     check = (d1[0]-time_interval,d1[1]-time_interval)
    #     if check not in completed_queued_calls.items():
    #             end_q.update({d1[0]-time_interval:d1[1]-time_interval})
    

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
    avg_GOS = calculate_erlangC(avg_offered_traffic)
    return(avg_call_duration,len(call_dict),avg_offered_traffic,avg_GOS,end_q_length)

# def calculate_GOS_erlangb():
#     all_data= []
#     iterator = bottom_range
#     while iterator <= top_range:
#         Ao = iterator
#         i = 1
#         n_factorial = 1
#         factorial_list=[]
#         numerator = 0
#         while i <= n:
#             n_factorial= n_factorial * i
#             factorial_list.append(n_factorial)
#             i +=1
#         numerator = (Ao**n)/factorial_list[n-1]
#         denominator=0
#         j = 1
#         while j <= len(factorial_list):
#             denominator +=(Ao**j)/factorial_list[j-1]
#             j+=1
#         denominator +=1
#         #print(denominator)
#         E1 = numerator/denominator
#         iterator +=1
#         all_data.append([Ao,E1*100])
#     return all_data

def calculate_erlangC(Ao):
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

# def calculate_ErlangC(Ao):
#     i = 1
#     n_factorial = 1
#     factorial_list=[]
#     numerator = 0
#     while i <= n:
#         n_factorial= n_factorial * i
#         factorial_list.append(n_factorial)
#         i +=1
#     try:
#         a_add_on = n/(n-Ao)
#     except ZeroDivisionError:
#         a_add_on = 0 
#     numerator = ((Ao**n)/factorial_list[n-1]) * a_add_on
#     denominator=0
#     j = 1
#     while j <= len(factorial_list):
#         denominator +=(Ao**j)/factorial_list[j-1]
#         j+=1
#     denominator +=1
#     denominator += ((Ao ** n)/factorial_list[n-1] * a_add_on)
#     E1 = numerator/denominator
#     return (E1*100)

if __name__ == "__main__":
    simulation_list = []

    print("Please wait a moment while the programme executes...")
    k=0
    while k < 1:
        call_dictionary,time_interval = create_random_variables()
        call_dur,calls,offered_traffic,GOS,dropped_calls =simulate_calls(call_dict2,time_interval)
        simulation_list.append([call_dur,calls,offered_traffic,GOS,dropped_calls])
        k+=1
   
    print("\nResults from Monte deCarlo simulation. Offered traffic varied with random number of calls and varied call length.\nConstant channels = 41")
    results_df = pd.DataFrame.from_records(simulation_list, columns=['Avg Call Duration',
                                                           'Avg No Calls',
                                                           'Avg Offered Traffic',
                                                           'Avg Prob Have Wait',
                                                           'Avg No Dropped Calls'])
    print(results_df.describe())
    results_df.describe().style.format('{:,}')
    
    # erlangC_list = []
    # erlangC_list = calculate_ErlangC()
    # resultsB = pd.DataFrame.from_records(erlangC_list, columns=[
    #                                                        'Avg Offered Traffic',
    #                                                        'Avg GOS'])
    # print("\n\nResults from Erlang B formula. Offered traffic varied not taking into account individual call length or number of calls.\nConstant channels = 41")
    # print(resultsB.describe())
    
    