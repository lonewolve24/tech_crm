# import uuid


# def generate_unique_code():
#     return str(uuid.uuid4()).replace('-', '').upper()[:10]


# print(generate_unique_code())


# def generate_receipt_number ():
#     import  datetime  
#     date = datetime.datetime.today().year

#     count = 0
#     count += 1
#     return f"REC-{date}-{str(count).zfill(4)}"

    


# print(generate_receipt_number())

def is_multiple_of_3(num):
    return num % 3 == 0

def is_multiple_of_5(num):
    return num % 5 == 0

def fizzbuzz(n):
    for i in range(1, n + 1):
        if is_multiple_of_3(i) and is_multiple_of_5(i):
            print("FizzBuzz")
        elif is_multiple_of_3(i):
            print("Fizz")
        elif is_multiple_of_5(i):
            print("Buzz")
        else:
            print(i)



n = 15

print (fizzbuzz(n))
