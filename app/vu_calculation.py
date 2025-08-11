marks = 81.19+77.50+76.78+76.01+75.50+71.09+73.69+74.87+72.81+63.10+62.03+70.23+70.58+72.12+68.11+71.73+72.17+67.68+66.98+68.49+72.89+68.84+73.19+67.05+72.15+70.93+63.03+72.40+72.05+69.12+69.29+61.80+73.26+67.43+72.87+62.86+69.42+73.23+85.00+68.00+73.39+73.15+71.97+83.37
total_marks = 4400

print("Total: ", total_marks)
print("Scored: ",marks)

percentage = (marks/total_marks)*100
print("Percentage: ", percentage)

if percentage >=90:
    print("You Scored: A+")
elif percentage >= 85:
    print("You Scored A")
elif percentage >=80:
    print("You Scored A-")
elif percentage >=75:
    print("You Scored B+")
elif percentage >=71:
    print("You Scored B")
elif percentage >= 68:
    print("You Scored B-")
