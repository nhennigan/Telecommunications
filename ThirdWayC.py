from scipy.stats import lognorm
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import random
import math
import statistics

#max number of calls handled
n = 41
#values for random call generation
maxValue, skewness, average_no_calls, std_deviation= 3600,0.5,99,27

#generate random varibales for simulation
def create_random_variables(no_calls):

    #generate random times in an hour for each call to start
    random_call_start_times = np.random.random_sample(size = no_calls)*3600

    #get random length of calls - comment out either line 22 or lines 24&25 to decide which distribution you want 
    #lognormal distribution
    random_call_length2 = lognorm.rvs(s =skewness,loc=average_no_calls, size=no_calls)

    #decaying exponential distribution 
    # random_call_length2 = np.random.random_sample(size = no_calls)
    # random_call_length2=[math.log(1-random_call_length2[c])/ -(1/900) for c in range(0,len(random_call_length2))]

    ###############
    #If using decaying exponential distribution, comment out these lines from 37 to 43
    #normalise data between 0-3600 seconds
    np.seterr(all='raise')
    try:
        random_call_length2 = random_call_length2 - min(random_call_length2)
        random_call_length2 = random_call_length2 / max(random_call_length2)
        random_call_length2 = random_call_length2 * maxValue   
    except FloatingPointError:
        print("Invalid value caught and programme continues")
    ###############

    #assign call length to call start time
    call_dict = {}
    call_dict = {int(random_call_start_times[p]):int(random_call_length2[p]) for p in range(0,no_calls)}

    return call_dict


#carry out Monte Carlo Simulation
def simulate_calls(call_dict):
    time, simultaneous_calls,call_index= 0,0,0
    skip_because_queued=[]
    queued_calls = {}
    #loop over one hour
    for time in range(0,maxValue):
        q = 0
        #attempt to add queued calls first due to FIFO
        while q < len(queued_calls):
            #If time = queued call start time, add it to simultaneous cal count, given there is room
            #Otherwise incrament its start time value in the queued by 1
            if queued_calls[q][0] == time:  
                if simultaneous_calls < n:
                    simultaneous_calls +=1
                else:
                    queued_calls[q][0]+=1
            #If queued call end time = time, take it off simultaneous call count
            if (queued_calls[q][0] + queued_calls[q][1]) == time:
                simultaneous_calls -=1
            q+=1

        for call in call_dict.items():
            #If time = call start time, add it to simultaneous calls count
            #otherwise queue and add it to queued_calls list
            if call[0] == time:
                if simultaneous_calls < n:
                    simultaneous_calls +=1
                else:
                    queued_calls[call_index] = list()
                    queued_calls[call_index].extend((call[0]+1,call[1]+1))
                    call_index +=1
                    skip_because_queued.append(call[0])
            #If call end time = time, take it off simultaneous call count
            #Check to make sure that call has not been queued
            if (call[1] + call[0]) == time:
                if call[0] in skip_because_queued:
                    continue
                simultaneous_calls -=1 
                
    #number of calls left on the queue at the end of the hour  
    no= len(call_dict.values())
    #get params to calculate GOS manually
    avg_call_duration = sum(call_dict.values())/no
    avg_offered_traffic = (avg_call_duration/maxValue)*no
    avg_GOS_from_queued=100*len(queued_calls)/no

    return(avg_offered_traffic,avg_GOS_from_queued)


def calculate_erlangc(bottom_range,top_range):
    graph_x2, graph_y2 = [],[]
    np.seterr(all='raise')
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
        try:
            a_add_on = n/(n-Ao)
        except ZeroDivisionError:
            a_add_on = 0 
        numerator = ((Ao**n)/factorial_list[n-1]) * a_add_on
        denominator=0
        j = 1
        #calculate denominator
        while j < len(factorial_list):
            denominator +=(Ao**j)/factorial_list[j-1]
            j+=1
        denominator +=1
        denominator += (((Ao ** n)/factorial_list[n-1])* a_add_on)
        #calculate GOS
        E1 = numerator/denominator
        iterator +=1
        graph_x2.append([Ao])
        graph_y2.append([E1*100])

    return graph_x2, graph_y2


if __name__ == "__main__":
    graph_x,graph_y,GOS_stdev=[],[],[]
    print("Please wait a moment while the programme executes...")

    #iterate through number of calls needed to produce all relevant Ao values
    for no_calls in range(40,160,4):
        k=0
        Ao_list,call_GOS=[],[]
        #repeat Ao value 50 times
        while k in range(0,100):
            call_dictionary = create_random_variables(no_calls)
            offered_traffic,GOS =simulate_calls(call_dictionary)
            Ao_list.append(offered_traffic)
            call_GOS.append(GOS)
            k+=1
        #get mean of 50 iterations at given Ao value
        graph_x.append(statistics.mean(Ao_list))
        graph_y.append(statistics.mean(call_GOS))
        GOS_stdev.append(statistics.stdev(call_GOS))
        
    #order x and y of graph in ascending order and plot monte carlo simulation
    xs, ys = zip(*sorted(zip(graph_x, graph_y)))
    plt.plot(xs,ys,label="Monte Carlo Simulation")
    
    #calculate points for +/- 1 standard deviation and plot
    plus_stdev = [ys[l]+ GOS_stdev[l] for l in range (0,len(GOS_stdev))]
    minus_stdev = [ys[l]- GOS_stdev[l] if ys[l]- GOS_stdev[l] >=0 else 0 for l in range (0,len(GOS_stdev))]
    plt.plot(xs,plus_stdev,label="Simulation +1 stdev",linestyle='--')
    plt.plot(xs,minus_stdev,label="Simulation -1 stdev",linestyle='--')
    
    #plot Erlang C graph
    graph_x2,graph_y2 = calculate_erlangc(10,40)
    plt.plot(graph_x2,graph_y2,label="Erlang C Formula")

    plt.xlabel("Ao (Erlangs)")
    plt.ylabel("GOS %")
    plt.title("Erlang C formula Vs Simulation with Lognormal Distribution of Call Lengths")
    #plt.title("Erlang C formula Vs Simulation with Decaing Exponential Distribution of Call Lengths")
    plt.legend(loc='upper left')
    plt.show()