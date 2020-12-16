import pandas as pd 

#offered traffic
Ao = 25
#max number of calls handled
n = 11
bottom_range = 25
top_range = 25


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
        E1 = numerator/denominator
        print("Offered traffic %s Erlang   GOS %s "%(iterator, E1*100))
        iterator +=1
        all_data.append([Ao,E1*100])
        
    return all_data

if __name__ == "__main__":
    erlangB_list = []
    erlangB_list = calculate_GOS_erlangb()
    resultsB = pd.DataFrame.from_records(erlangB_list, columns=[
                                                           'Avg Offered Traffic',
                                                           'Avg GOS'])
    print("\n\nResults from Erlang B formula. Offered traffic varied not taking into account individual call length or number of calls.\nConstant channels = 41")
    print(resultsB.describe())