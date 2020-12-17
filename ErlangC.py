import pandas as pd 
import numpy as np

#offered traffic
Ao = 25
#max number of calls handled
n = 41
#range of traffic
bottom_range = 6
top_range = 50

def calculate_erlangc():
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
        print("Offered traffic %s Erlang   GOS %s "%(iterator, E1*100))
        iterator +=1
        all_data.append([Ao,E1*100])
        
    return all_data

if __name__ == "__main__":
    erlangC_list = []
    erlangC_list = calculate_erlangc()
    resultsC = pd.DataFrame.from_records(erlangC_list, columns=[
                                                           'Avg Offered Traffic',
                                                           'Avg GOS'])
    print("\n\nResults from Erlang C formula. Offered traffic varied not taking into account individual call length or number of calls.\nConstant channels = 41")
    print(resultsC.describe())