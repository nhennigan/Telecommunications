
from scipy.stats import skewnorm
from scipy.stats import lognorm
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import random

#offered traffic
Ao = 25
#max number of calls handled
n = 2
bottom_range = 10
top_range = 30

average_no_calls=99
std_deviation = 55
max_calls=160

# no_calls = np.random.normal(average_no_calls,std_deviation)
# print(no_calls)

no_calls = int(random.normalvariate(average_no_calls,std_deviation))
print(no_calls)
#maybe put in a check here to make sure the random number generated is not negative

#times of each call starting 

#get random length of calls 
numValues = 1000
maxValue = 3600
skewness = 0.3
#mean = 15

# random = skewnorm.rvs(a = skewness,loc=maxValue, size=numValues)  #Skewnorm function
# random_call_length = lognorm.rvs(s = skewness,loc= 0,scale = 1,size=no_calls)
# random_call_length = random_call_length - min(random_call_length)
# random_call_length = random_call_length / max(random_call_length)
# random_call_length = random_call_length * maxValue   

random_call_length2 = lognorm.rvs(s = skewness,loc= 900,scale = 1,size=no_calls)
random_call_length2 = random_call_length2 - min(random_call_length2)
random_call_length2 = random_call_length2 / max(random_call_length2)
random_call_length2 = random_call_length2 * maxValue   

random_call_lengths_int = []
for value in random_call_length2:
    random_call_lengths_int.append(int(value)) 
    #maybe put in a check that it doesn't go over 3600 in length

#print(random_call_lengths_int)
print(len(random_call_lengths_int))

p = 0
time_between_calls = int(3600/no_calls)
time=0
counter = 0
call_dict = {}
while p < no_calls:
    counter += 1
    #print("call number %d will start at %d seconds into hour"%(p,time))
    time += time_between_calls
    
    #print(random_call_lengths_int[p])
    call_dict.update({time:random_call_lengths_int[p]})
    p+=1
print(call_dict)

time = 0
simultaneous_calls=0
call_dict2 = {
    2:12,
    5:5,
    8:20,
    11: 10
}

#print(call_dict.values())
 
#print(call_dict2)
#print("sim calls %s"%simultaneous_calls)
dropped_calls={}
skip_because_dropped=[]
#print("len call dict %d"%len(call_dict))
while time < 36:
    #print("sim calls %s"%simultaneous_calls)
    for call in call_dict2.items():
        #print(call)
        # for call_start_time, call_length in call.items():
            # #print(call_start_time[0])
        # print(call[0])
        # print(call[1])
        if call[0] == time:
            print("got to true")
            if simultaneous_calls < n:
                print("adding one to the pack")
                simultaneous_calls +=1
            else:
                print("Max number of calls reached")
                dropped_calls.update({call[0]:call[1]})
                skip_because_dropped.append(call[0])
                #call_dict.popitem()
                #continue
        print("skip list")
        print(skip_because_dropped)

        if (call[1] + call[0]) == time:
            print("got to second end time check")
            if call[0] in skip_because_dropped:
                "this call was not made in the first place"
                continue
                simultaneous_calls -=1
            print("call ended")
            
    print("number of calls at %d seconds: %d"%(time,simultaneous_calls))
            # #print(call)
            # # print(call[0])
            # # print(call[1])
            # # print(call.values())
    time +=1  
print("number of calls at %d seconds: %d"%(time,simultaneous_calls))
#print("len call dict after %d"%len(call_dict))
print(dropped_calls)
# random = random - min(random)      #Shift the set so the minimum value is equal to zero.
# random = random / max(random)      #Standadize all the vlues between 0 and 1. 
# random = random * maxValue         #Multiply the standardized values by the maximum value.

# #Plot histogram to check skewness
# plt.hist(random,30,density=True, color = 'red', alpha=0.1)
# plt.show()

plt.hist(random_call_length2,30,density=True, color = 'red', alpha=0.1)
plt.show()

# iterator = bottom_range
# while iterator <= top_range:
    # Ao = iterator
    # print("Offered traffic %s Erlang"%iterator)
    # i = 1
    # n_factorial = 1
    # factorial_list=[]
    # numerator = 0
    # while i <= n:
        # n_factorial= n_factorial * i
        # factorial_list.append(n_factorial)
        # i +=1
    # #print(factorial_list)
    # numerator = (Ao**n)/factorial_list[n-1]
    # #print("num %s"%numerator)
    # denominator=0
    # j = 1
    # while j <= len(factorial_list):
        # # print("J %s"%j)
        # # print("power of equals %s"%Ao**j)
        # # print("fact list val %s"%factorial_list[j-1])
        # # print((Ao**j)/factorial_list[j-1])
        # denominator +=(Ao**j)/factorial_list[j-1]
        # j+=1
        # #print("denom %s"%denominator)
    # denominator +=1
    # #print(denominator)
    # E1 = numerator/denominator
    # print("GOS %s "%(E1*100))
    # iterator +=1