def f(a):
    print(id(a))
    print(a)
    a[0]= 1 

a = [10]
print(id(a))
f(a)


print(a)