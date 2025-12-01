
name=input("What is your name?")

if name=="sab":
    print("You are getting into U chicago")
else:
    print("hello " + name + " i know where u live")




if name=="soph":
    while True:
        question=input("does sab have explosive scat? ")

        if question== "yes":
            print("you r verry correct about that ans sab should go to dr wiesberg right away")
            break

        elif question== "no":
            print( "you r very wrong and sab DOES have explosive scat because i saw her wiping it with a leaf in the forest once so she needs to go to dr wiesberg right away")
            break
        
        else:
            print("put yes or no please")

    lie_count = 0
    while True:
        question2=int(input ("how often do u scat per day? "))
        if question2== 4:
            print("You are a normal scatter")
            print("look to ur right now")
            break
        elif question2<=3:
            lie_count += 1
            print("We know you are lying, what is the real ammount")
            print("look to ur right now")
            if lie_count >= 2:
                print("STOP THE LYING RIGHT NOW")
        elif question2>=5:
            print("you scat too much and you are breaking down the ozone layer with your toxic scat fumes and carbon dioxide and killing the planet")
            print("look to ur right now")
            break
        else:
            print("WHAT IS WRONG WITH YOU?? YOU ARE KILLING THE PALENT YOU MURDDERER")
            break
            
    


