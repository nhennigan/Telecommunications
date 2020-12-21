from scipy.stats import lognorm
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import random
import math

#max number of calls handled
n = 41

#values for random call generation
maxValue = 3600
skewness = 0.5
average_no_calls=99
std_deviation = 27

graph_x2=[]
graph_y2=[]

#generate random varibales for simulation
def create_random_variables():
    #generate random # of calls from normal distribution
    no_calls = int(random.normalvariate(average_no_calls,std_deviation))
    #if no_calls invalid set to standard avergae # calls not in busy hour
    if no_calls <= 0:
        no_calls = 67

    #get random length of calls 
    #random_call_length2 = lognorm.rvs(s =skewness,loc=average_no_calls, size=no_calls)
    random_call_length2 = np.random.random_sample(size = no_calls)
    c = 0
    while c < len(random_call_length2):
        x = 1 - random_call_length2[c]
        random_call_length2[c] = math.log(x)/ -(1/900)
        c+=1
    #checks to make sure call lenght is ok
    if (len(random_call_length2) == 0):
        random_call_length2 = [0.1,0.2,0.3]
    for call in random_call_length2:
        if call < 0 or np.isnan(call):
            random_call_length2[call] = 0.1 

    np.seterr(all='raise')
    #normalise data between 0-3600 seconds
    # try:
    #     random_call_length2 = random_call_length2 - min(random_call_length2)
    #     random_call_length2 = random_call_length2 / max(random_call_length2)
    #     random_call_length2 = random_call_length2 * maxValue   
    # except FloatingPointError:
    #     print("Invalid value caught and programme continues")

    #put random call lengths into a list parsed into ints
    random_call_lengths_int = []
    for value in random_call_length2:
        if math.isnan(value):
            random_call_lengths_int.append(900)
            continue
        random_call_lengths_int.append(int(value)) 

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
    skip_because_dropped=[]
    queued_calls = {}
    completed_queued_calls = []
    call_index=0
    end_q_length=0

    while time < maxValue:
        q = 0
        #attempt to add queued calls first due to FIFO
        while q < len(queued_calls):
            #If time = queued call start time, add it to simultaneous cal count, given there is room
            #Otherwise incrament its start time value in the queued by 1
            if queued_calls[q][0] == time:  
                if simultaneous_calls < n:
                    simultaneous_calls +=1
                    completed_queued_calls.append(queued_calls[q][0])
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
                    skip_because_dropped.append(call[0])
            #If call end time = time, take it off simultaneous call count
            #Check to make sure that call has not been queued
            if (call[1] + call[0]) == time:
                if call[0] in skip_because_dropped:
                    continue
                simultaneous_calls -=1
        time +=1  
    #number of calls left on the queue at the end of the hour  
    end_q_length = len(queued_calls) - len(completed_queued_calls)
    
    #get params to calculate GOS manually
    avg_call_duration = sum(call_dict.values())/len(call_dict.values())
    avg_offered_traffic = (avg_call_duration/maxValue)*len(call_dict.values())
    avg_GOS_from_queued=100*len(queued_calls)/len(call_dict)

    return(avg_call_duration,len(call_dict),avg_offered_traffic,avg_GOS_from_queued,end_q_length)


def calculate_erlangc(bottom_range,top_range):
    global graph_x2
    global graph_y2
    np.seterr(all='raise')
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
        #print("Offered traffic %s Erlang   GOS %s "%(iterator, E1*100))
        iterator +=1
        all_data.append([Ao,E1*100])
        graph_x2.append([Ao])
        graph_y2.append([E1*100])


if __name__ == "__main__":
    simulation_list = []
    graph_x=[]
    graph_y=[]
    print("Please wait a moment while the programme executes...")
    k=0
    while k < 500:
        call_dictionary = create_random_variables()
        call_dur,calls,offered_traffic,GOS,unasnwered_calls =simulate_calls(call_dictionary)
        graph_x.append(offered_traffic)
        graph_y.append(GOS)
        simulation_list.append([call_dur,calls,offered_traffic,GOS,unasnwered_calls])
        k+=1
   
    print("\nResults from Monte deCarlo simulation. Offered traffic varied with random number of calls and varied call length.\nConstant channels = 41")
    results_df = pd.DataFrame.from_records(simulation_list, columns=['Avg Call Duration',
                                                           'Avg No Calls',
                                                           'Avg Offered Traffic',
                                                           'Avg GOS',
                                                           'Avg No Unanswered Calls'])
    print(results_df.describe())
    
    xs, ys = zip(*sorted(zip(graph_x, graph_y)))
   
    calculate_erlangc(results_df['Avg Offered Traffic'].min(),results_df['Avg Offered Traffic'].max())
    plt.plot(xs,ys)
    plt.plot(graph_x2,graph_y2)
    plt.xlabel("Ao")
    plt.ylabel("GOS")
    plt.title("Erlang C formula Vs Simulation with Decaying Exponential")
    plt.show()