 # a coroutine is a specialized function that can pause its execution and resume later

# example 
import time

student = ["gajender","ramesh","ram","abhay","ajay"]
def read():
    time.sleep(3)
    data = student
    while True :
        name = yield(data)
        if name in data:
            print("student find")
        else:
            print("student not found")

search = read()
print("Read all student")
next(search)
print("read done")
search.send("gajender")
search.send("name")
search.send("abhay")



