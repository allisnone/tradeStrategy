#list USAGE
print('list--------------------')
li=[1.0,0.2,0.5,0.1,1.8]

li.sort()
print(li)
li.sort(reverse=True)
print(li)

print('dict--------------------')

di={'a':1.1,'b':0.8,'c':2.5,'d':0.4}
#print(di.has_key('a'))  #python2
print('a' in di) #python3

print(min(di))
print(max(di))

print(min(di.values()))
print(max(di.values()))
print(sum(di.values()))


di_key_li=di.keys()
print('di_key_list=',di_key_li,type(di_key_li))
di_value_list=di.values()
print('di_value_list=',di_value_list,type(di_value_list))
#di_value_list.sort(reverse=True)

di_item_list=di.items()

di_sort_by_key=sorted(di.items(),key=lambda di:di[0])
print('di_sort_by_key=',di_sort_by_key)

di_sort_by_value=sorted(di.items(),key=lambda di:di[1])
print('di_sort_by_value=',di_sort_by_value)

di_sort_by_value=sorted(di.items(),key=lambda di:di[1],reverse=True)
print('di_sort_by_value=',di_sort_by_value)


