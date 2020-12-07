########################################################################################################################
# Class: Computer Networks
# Date: 02/03/2020
# Lab0: Getting Started with Python
# Goal: Learning the basics of Python
# Student Name: Brad Patrick Peraza
# Student ID: 916768260
# Student Github Username: eraaaza
# Instructions: Complete the TODO sections for each problem
# Guidelines: Read each problem carefully, and implement them correctly. Grade is based on lab correctness/completeness
#               No partial credit will be given.
#               No unit test are provided for lab #0
########################################################################################################################

########################## Problem 0: Print  ###########################################################################
"""
Print your name, student id and Github username
Sample output:
Name: Jose
SID: 91744100
Github Username:
"""
name = "Brad Patrick Peraza" # TODO: your name
SID = 916768260 # TODO: your student id
git_username = "eraaaza" # TODO: your github username
print(name)
print(SID)
print(git_username)
print('\n')


########################## Problem 1: Processing user input ############################################################
"""
Accept two int values from the user, and print their product. If their product is greater than 500, 
then print their sum

Sample output:
Enter the first integer: 2
Enter the second integer: 4
Result is 8
Enter the first integer: 2
Enter the second integer: 1000
Result is 1002
"""
print("Problem 1 ********************") # problem header (don't modify)
# TODO: your code here
# asks and stores the user's first value, converts value to integer
value1 = int(input("Enter the first integer:\n"))

print(f'First integer is: {value1}')

# asks and stores the user's second value, converts value to integer
value2 = int(input("Enter the second integer:\n"))

print(f'Second integer is: {value2}')

# take the sum of the both values
value3 = value1 * value2

if value3 > 500:
    # if sum of both values is greater than 500 then add the two values
    print(f"This result is {value1 + value2}")
else:
    print(f"The result is {value3}")

########################## Problem 2: String Processing ##############################################################
"""
Given a string print the number of times the string "Alice" appears anywhere in the given string

For example, given the string: "Alice and Bob go to the same school. They learned today in class how to treat a lice 
infestation, and Alice found the lecture really interesting" 
the sample output would be: 'Alice' found 2 times. 
"""
print("Problem 2 ********************") # problem header (don't modify)
# the given string
myString = ("Alice and Bob go to the same school. They learned today in class how to treat a lice" 
           "infestation, and Alice found the lecture really interesting")
# TODO: your code here
# count() returns the count of how many times an object occurs in a string or list
print(f"'Alice' is found {myString.count('Alice')} times in the passage\n")



########################## Problem 3: Loops ############################################################################
"""
Given a list of numbers iterate over them and output the sum of the current number and previous one.

Given: [5, 10, 24, 32, 88, 90, 100] 
Outputs: 5, 15, 34, 56, 120, 178, 190.
"""
print("Problem 3 ********************") # problem header (don't modify)
numbers = [5, 10, 24, 32, 88, 90, 100]
# TODO: your code here
# create a sequence of numbers equal to the length of the the list
for i in range(len(numbers)):
    if i == 0:
        print(numbers[i])
    else:
        print(numbers[i - 1] +numbers[i])

########################## Problem 4: Functions/Methods/Lists ##########################################################
"""
Create the method mergeOdds(l1, l2) which takes two unordered lists as parameters, and returns a new list with all the 
odd numbers from the first a second list sorted in ascending order. Function signature is provided for you below

For example: Given l1 = [2,1,5,7,9] and l2 = [32,33,13] the function will return odds = [1,5,7,9,13,33] 
"""
print("Problem 4 ********************") # problem header (don't modify)
# function skeleton
def merge_odds(l1, l2):
    odds = []
    # TODO: your code here
    for i in range(len(l1)):
        if l1[i] % 2 == 1:
            # if the object in the i position of l1 is odd, append to odds list
            odds.append(l1[i])

    for i in range(len(l2)):
        if l2[i] % 2 == 1:
            # if the object in the i position of l2 is odd, append to odds list
            odds.append(l2[i])

    # sort() sorts list in ascending order, unless criteria is added
    odds.sort()
    return odds

l1 = [2,1,5,7,9]
l2 = [32,33,13]
odds = merge_odds(l1, l2)
print(odds)

########################## Problem 5: Functions/Methods/Dictionaries ###################################################
"""
Refactor problem #4 to return a python dictionary instead a list where the keys are the index of the odd numbers in l1,
and l2, and the values are the odd numbers. 

For example: Given l1 = [2,1,5,7,9] and l2 = [32,33,13] the function will return odds = {1: [1, 33], 2: [5,13], 3: [7], 4: [9]} 
"""
print("Problem 5 ********************") # problem header
# function skeleton
def merge_odds(l1, l2):
    odds = {}
    # TODO: your code here
    for i in range(len(l1)):
        # if odd
        if l1[i] % 2 == 1:
            # store i as key and object in list as value in dictionary
            odds[i] = [l1[i]]

    for i in range(len(l2)):
        # if odd
        if l2[i] % 2 == 1:
            # if the key is not found in our dictionary
            if i not in odds:
                # store i as key and object in list as value in dictionary
                odds[i] = [l2[i]]
            else:
                # if key already found append the new value to that key in our dictionary
                odds[i].append(l2[i])

    return odds

l1 = [2,1,5,7,9]
l2 = [32,33,13]
odds = merge_odds(l1, l2)
print(odds)
