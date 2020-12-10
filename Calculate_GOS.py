#offered traffic
Ao = 25
#max number of calls handled
n = 41
bottom_range = 10
top_range = 30


from scipy.stats import skewnorm
from scipy.stats import lognorm
import matplotlib.pyplot as plt


#get random length of calls 
numValues = 1000
maxValue = 60
skewness = 0.45
#mean = 15

random = skewnorm.rvs(a = skewness,loc=maxValue, size=numValues)  #Skewnorm function
random2 = lognorm.rvs(s = skewness,scale = 1,size=numValues)
random2 = random2 - min(random2)
random2 = random2 / max(random2)
random2 = random2 * maxValue   

random = random - min(random)      #Shift the set so the minimum value is equal to zero.
random = random / max(random)      #Standadize all the vlues between 0 and 1. 
random = random * maxValue         #Multiply the standardized values by the maximum value.

#Plot histogram to check skewness
plt.hist(random,30,density=True, color = 'red', alpha=0.1)
plt.show()

plt.hist(random2,30,density=True, color = 'red', alpha=0.1)
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