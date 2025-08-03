def binarySearch(ls,value,low,high):
    if high <= low:
        if value > ls[low]:
            return low+1
        else:
            return low
    else:
        mid = (low + high)//2
        if value == ls[mid]:
            return mid
        if value > ls[mid]:
            return binarySearch(ls,value,mid+1,high)
        else:
            return binarySearch(ls,value,low,mid-1)

def binaryInsertionSort(ls):

    for k in range(1,len(ls)):
       

        #binary partition part
        i = binarySearch(ls,ls[k],0,k)

        if i!= k:
            tmp = ls[k]
            for j in range(k-1,i-1,-1):
                ls[j+1] = ls[j]
            ls[i] = tmp
    return ls

print(binaryInsertionSort([9, 3, 3,4, 5]))


    