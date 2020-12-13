
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
skewness = 0.4

average_no_calls=99
std_deviation = 55
#max_calls=160


# print(no_calls)

def create_random_variables():

    # phi = (std_deviation ** 2 + average_no_calls **2)
    # mu = np.log(average_no_calls **2 / phi)
    # sigma = (np.log(phi **2/ average_no_calls **2)) **0.5
    # generated_pop = np.random.lognormal(mu,sigma,10000)

    # generated_pop = generated_pop - min(generated_pop)
    # generated_pop = generated_pop / max(generated_pop)
    # generated_pop = generated_pop * maxValue   


    # bins = np.arange(0,51,1)
    # plt.hist(generated_pop, bins=bins)
    # plt.show()
    #get random number of calls
    #no_calls = np.random.normal(average_no_calls,std_deviation)
    no_calls = int(random.normalvariate(average_no_calls,std_deviation))
    #print(no_calls)
    if no_calls <= 0:
        no_calls = 67
    #maybe put in a check here to make sure the random number generated is not negative

    #get random length of calls 
    random_call_length2 = lognorm.rvs(s =skewness,loc=average_no_calls, size=no_calls)

    #random_call_length2 = lognorm.rvs(std_deviation,size=no_calls)*np.exp(average_no_calls)
    #print(random_call_length2)
    if (len(random_call_length2) == 0):
        random_call_length2 = [0.1,0.2,0.3]
    for call in random_call_length2:
        if call < 0 or np.isnan(call):
            random_call_length2[call] = 0.1 

    #print(random_call_lengths_int)
    np.seterr(all='raise')
    try:
        random_call_length2 = random_call_length2 - min(random_call_length2)
        random_call_length2 = random_call_length2 / max(random_call_length2)
        random_call_length2 = random_call_length2 * maxValue   
    except FloatingPointError:
        print("Invalid value caught and programme continues")

    #print(np.mean(random_call_length2))

    # plt.hist(random_call_length2,30,density=True, color = 'red', alpha=0.1)
    # plt.show()

    #put random call lengths into a list parsed into ints
    random_call_lengths_int = []
    for value in random_call_length2:
        if math.isnan(value):
            #print(value)
            random_call_lengths_int.append(900)
            continue
        random_call_lengths_int.append(int(value)) 
        #maybe put in a check that it doesn't go over 3600 in length

    #print(len(random_call_lengths_int))

    p = 0
    time_between_calls = int(maxValue/no_calls)
    time=0
    counter = 0
    call_dict = {}

    #assign call length to call start time
    while p < no_calls:
        counter += 1
        #print("call number %d will start at %d seconds into hour"%(p,time))
        time += time_between_calls

        #print(random_call_lengths_int[p])
        call_dict.update({time:random_call_lengths_int[p]})
        p+=1
    #print(call_dict)
    return call_dict



# call_dict2 = {
    # 2:12,
    # 5:5,
    # 8:20,
    # 11: 10
# }

 
#print(call_dict2)
#print("sim calls %s"%simultaneous_calls)
def simulate_calls(call_dict):
    time = 0
    simultaneous_calls=0
    dropped_calls={}
    skip_because_dropped=[]
    #print("len call dict %d"%len(call_dict))
    while time < maxValue:
        #print("sim calls %s"%simultaneous_calls)
        for call in call_dict.items():
            #print(call)
            # for call_start_time, call_length in call.items():
                # #print(call_start_time[0])
            # print(call[0])
            # print(call[1])
            if call[0] == time:
                #print("got to true")
                if simultaneous_calls < n:
                    #print("adding one to the pack")
                    simultaneous_calls +=1
                else:
                    #print("Max number of calls reached")
                    dropped_calls.update({call[0]:call[1]})
                    skip_because_dropped.append(call[0])
                    #call_dict.popitem()
                    #print("skip list")
                    #print(skip_because_dropped)

            if (call[1] + call[0]) == time:
                #print("got to second end time check")
                #print(call[0] in skip_because_dropped)
                if call[0] in skip_because_dropped:
                    #print("this call was not made in the first place")
                    continue
                simultaneous_calls -=1
                #print("call ended")

        #print("number of calls at %d seconds: %d"%(time,simultaneous_calls))
        time +=1  
    #print("number of calls at %d seconds: %d"%(time,simultaneous_calls))
    #print("len call dict after %d"%len(call_dict))
    #print(dropped_calls)
    #print("no dropped: %d"%len(dropped_calls))

    avg_call_duration = sum(call_dict.values())/len(call_dict.values())
    avg_offered_traffic = (avg_call_duration/maxValue)*len(call_dict.values())

    #print(avg_call_duration)
    avg_GOS = calculate_GOS(avg_offered_traffic)
    return(avg_call_duration,len(call_dict),avg_offered_traffic,avg_GOS,len(dropped_calls))

def calculate_GOS_erlangb():
    all_data= []
    iterator = bottom_range
    while iterator <= top_range:
        Ao = iterator
        #print("Offered traffic %s Erlang"%iterator)
        i = 1
        n_factorial = 1
        factorial_list=[]
        numerator = 0
        while i <= n:
            n_factorial= n_factorial * i
            factorial_list.append(n_factorial)
            i +=1
        #print(factorial_list)
        numerator = (Ao**n)/factorial_list[n-1]
        #print("num %s"%numerator)
        denominator=0
        j = 1
        while j <= len(factorial_list):
            # print("J %s"%j)
            # print("power of equals %s"%Ao**j)
            # print("fact list val %s"%factorial_list[j-1])
            # print((Ao**j)/factorial_list[j-1])
            denominator +=(Ao**j)/factorial_list[j-1]
            j+=1
            #print("denom %s"%denominator)
        denominator +=1
        #print(denominator)
        E1 = numerator/denominator
        #print("GOS %s "%(E1*100))
        iterator +=1
        all_data.append([Ao,E1*100])
    return all_data

def calculate_GOS(Ao):
    #print("Offered traffic %s Erlang"%Ao)
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
    E1 = numerator/denominator
    #print("GOS %s "%(E1*100))
    return (E1*100)

if __name__ == "__main__":
    simulation_list = []

    print("Please wait a moment while the programme executes...")
    k=0
    while k < 100:
        call_dictionary = create_random_variables()
        call_dur,calls,offered_traffic,GOS,dropped_calls =simulate_calls(call_dictionary)
        simulation_list.append([call_dur,calls,offered_traffic,GOS,dropped_calls])
        k+=1
    #print(simulation_list)
    # call_dictionary = create_random_variables()
    # call_dur,calls,offered_traffic,GOS =simulate_calls(call_dictionary)
    print("\nResults from Monte deCarlo simulation. Offered traffic varied with random number of calls and varied call length.\nConstant channels = 41")
    results_df = pd.DataFrame.from_records(simulation_list, columns=['Avg Call Duration',
                                                           'Avg No Calls',
                                                           'Avg Offered Traffic',
                                                           'Avg GOS',
                                                           'No Dropped Calls'])
    print(results_df.describe())
    results_df.describe().style.format('{:,}')
    
    erlangB_list = []
    erlangB_list = calculate_GOS_erlangb()
    resultsB = pd.DataFrame.from_records(erlangB_list, columns=[
                                                           'Avg Offered Traffic',
                                                           'Avg GOS'])
    print("\n\nResults from Erlang B formula. Offered traffic varied not taking into account individual call length or number of calls.\nConstant channels = 41")
    print(resultsB.describe())
    
    