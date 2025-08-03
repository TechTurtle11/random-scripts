def countingSort(a,k):
    c = [0 for i in range(k)]
    
    for j in range(len(a)):
        c[a[j]] +=1
    print(c)
    for i in range(k):
        c[i] = c[i] +c[i-1]
    print(c)
    b = [0 for i in range(k)]
    for j  in range(len(a)-1,0,-1):
        b[c[a[j-1]]] = a[j-1]
        c[a[j-1]] = c[a[j-1]] -1

    print(c)

    return b
ls = [3,2,9,2,6,2,9,7]
print(ls)
print(countingSort(ls,max(ls)+2))