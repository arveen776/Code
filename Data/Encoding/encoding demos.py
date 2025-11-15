b1 = 0b01000010  # 'B'
b2 = 0b00100000  # ' ' (space)
b3 = 0b01000001  # 'A'

data = bytes([b1, b2, b3])

#print(data) 
#print(data.decode())  


#Going in reverse

text = "What is the reason for doing anything as it is in this moment in time? Alpha Beta Gamma Delta."

encode = text.encode()

print(list(encode))

for byte in encode:
    print(f"{byte:08b}")
