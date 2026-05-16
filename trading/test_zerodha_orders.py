import re

# # valuate-Postfix-Expression-using-Stack
# ["2","1","+","3","*"]
# ["4","2","/","5","-"]
# ["2","1","+","3","*","5","+"]
# # output = 9


# Input
# string = "aaadaa"
# substring = "aa"

# # Find all overlapping occurrences
# pattern = f"(?={substring})"  # Positive lookahead to find overlapping matches
# print(pattern)
# matches = re.finditer(pattern, string)

# print(pattern)
# print(matches)
# results = []
# for match in matches:
#     start = match.start()
#     end = start + len(substring) - 1
#     results.append((start, end))
# for result in results:
#     print(result)

# (0, 1)
# (1, 2)
# (4, 5)
#==========

class UserMainCode(object):
    @classmethod
    def therow(cls, input1):
        # Calculate dimensions
        row = 3
        col = len(input1) // 3
        
        # Reshape the 1D array into a 2D matrix
        matrix = []
        n = 0
        for i in range(row):
            row_data = []
            for j in range(col):
                row_data.append(input1[n])
                n += 1
            matrix.append(row_data)
        
        # Print the matrix
        # print(matrix)
        # for i in range(row):
        #     for j in range(col):
        #         print(matrix[i][j], end=" ")
        #     print()
        
        return matrix
    @classmethod
    def multiply(cls, matrix1, matrix2):
        """
        Multiply two matrices
        matrix1: 3xN matrix
        matrix2: 3xM matrix
        Returns: 3xM matrix (matrix1^T * matrix2) or custom multiplication
        """
        # Check if matrices have compatible dimensions
        if len(matrix1) != len(matrix2):
            raise ValueError("Matrices must have the same number of rows")
        
        # Get dimensions
        rows1 = len(matrix1)
        cols1 = len(matrix1[0]) if matrix1 else 0
        cols2 = len(matrix2[0]) if matrix2 else 0
        
        # Initialize result matrix with zeros
        result = [[0 for _ in range(cols2)] for _ in range(rows1)]
        
        # Perform multiplication (matrix1 * matrix2^T or matrix1^T * matrix2?)
        # Based on your dimensions, you might want matrix1^T * matrix2
        # Let's assume you want element-wise multiplication of rows
        for i in range(rows1):
            for j in range(cols2):
                for k in range(cols1):
                    result[i][j] += matrix1[i][k] * matrix2[i][j]
        
        return result

input1 = [5, 1, 0, 3, -1, 2, 4, 0, -1]
input2 = [1, 2, 2, 1, 4, 5]

# # Test with input1
# A = UserMainCode.therow(input1)
# print("\nResult matrix A:", A)

# B = UserMainCode.therow(input2)
# print("\nResult matrix B:", B)

# print("Matrix A (3x3):")
# for row in A:
#     print(row)

# print("\nMatrix B (3x2):")
# for row in B:
#     print(row)


import numpy as np

A = np.array(input1).reshape(3, 3)
print(A)
B = np.array(input2).reshape(3, 2)
print(B)


C = np.dot(A, B)

print("\nUsing NumPy C:")
print(C)

D = C.T
print("\nReshaped D (3x2):")
print(D)

E = np.concatenate((A, B, C), axis=1)
print("\nConcatenated E (3x5):")
print(E)

F_list = D.flatten().tolist()
print(F_list)
print(type(F_list))
F_list.append(0)
print("\nF_list (3x2):")
print(F_list)

new_row = np.sum(E, axis=1)
print("\nNew row (1x5):")
print(new_row)
##
nums = [2, 7, 4, 6]
target = 9

def two_sum_1_based(nums, target):
    seen = {}
    for i, n in enumerate(nums, start=1):  # 1-based index
        need = target - n
        if need in seen:
            return [seen[need], i]
        seen[n] = i
    return []

output = two_sum_1_based(nums, target)
print(output)

print("=============================")
dic = {'a': 12, 'b': 21, 'c': 3}

# sorted_keys = {key:val for key,val in sorted(dic.items(), key=lambda item: item[1])}
# print(sorted_keys)

# d = [
#     {'name':'gajender','age':89,'val':12},
#     {'name':'abhay','age':89,'val':12},
#     {'name':'amit','age':89,'val':12},
#     {'name':'shiva','age':89,'val':12},
# ]

# # sorted d by name
# sorted_d = sorted(d, key=lambda x: x['name'])
# print(sorted_d)



# Perform multiplication
# try:
#     result = UserMainCode.multiply(A, B)
#     print("\nResult of multiplication (3x2):")
#     for row in result:
#         print(row)
# except ValueError as e:
#     print(f"\nError: {e}")

# If you want to test with input2, you'd need to calculate different dimensions
# For input2 with 6 elements, you could have 3 rows and 2 columns


l = ["eat", "tea", "tan", "ate", "nat", "bat"]

#  [
#     ["eat", "tea", "ate"],
#     ["tan", "nat"],
#     ["bat"]
# ]

# unique = []
# for item in l:
#     sub_list = []
#     item_sort = sorted(item)
#     item_sort_string = "".join(item_sort)
#     if item_sort_string not in unique:
#         unique.append(item_sort_string)
# final = []
# for item in unique:
#     sub_list = []
#     for item2 in l:
#         item2_string = "".join(sorted(item2))
#         if item == item2_string:
#             sub_list.append(item2)
    
#     final.append(sub_list)
# print(final)
        

l = ["eat", "tea", "tan", "ate", "nat", "bat"]
# output like 
# [
#     ["eat", "tea", "ate"],
#     ["tan", "nat"],
#     ["bat"]
# ]

#################### generator program for even no
n = 50
my_list = [ x for x in range(1,n+1)]

def even_numbers_generator(numbers_list):
    for n in numbers_list:
        if n%2==0:
            yield n

evens_gen = even_numbers_generator(my_list)

for item in evens_gen:
    print(item)

#######################
from collections import defaultdict

l = ["eat", "tea", "tan", "ate", "nat", "bat"]

def group_anagrams(words):
    anagram_dict = defaultdict(list)
    print(anagram_dict)
    
    for word in words:
        # Sort the word to create a key
        sorted_word = ''.join(sorted(word))
        print(sorted_word)
        anagram_dict[sorted_word].append(word)
        print(anagram_dict)
    
    return list(anagram_dict.values())

result = group_anagrams(l)
print(result)


# models = {
#     "A": {"performance": 8.92, "accuracy": 94.3, "speed": 4.3},
#     "B": {"performance": 68.54, "accuracy": 99.83, "speed": 6.9},
#     "C": {"performance": 44.87, "accuracy": 89.32, "speed": 7.9}
# }
#  {
#     "performance": "{"A": 8.92, "B": 68.54", "C": 44.87},
#     "accuracy": "{"A": 1, "B": 2", "C": 4},
#     "speed": "{"A": 1, "B": 2", "C": 4},
#     }
transposed = {}
original_models = {
    "A": {"performance": 8.92, "accuracy": 94.3, "speed": 4.3},
    "B": {"performance": 68.54, "accuracy": 99.83, "speed": 6.9},
    "C": {"performance": 44.87, "accuracy": 89.32, "speed": 7.9}
}

for model, metrics  in original_models.items():
    for metric, value  in metrics.items():
        if metric not in transposed:
            transposed[metric] = {}
        transposed[metric][model] = value
        
            
        
print(transposed)
