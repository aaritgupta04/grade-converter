list1=[]
task=input("Enter a student name.")
list1.append(task)

while True:
  choise=int(input("---To-Do list Menu---\n1.View students\n2.Add a student\n3.Remove a student\n4.Count the average" \
  "\n5.close tab\n6.choose an option(1-5)"))
  if choise==1:
    for i in list1:
      print(i)
      

  elif choise==2:
    task=input("enter the name of the student")
    list1.append(task)
    print("student has been added")
    

  elif choise==3:
    task=input("element_to_be_removed")
    list1.remove(task)
    print("student has been removed")
    

  elif choise==4:
    result=float(input("enter your maths score"))
    result1=float(input("enter your eng score"))
    result2=float(input("enter your sports score"))
    result3=float(input("enter your drawing class score"))
    result4=float(input("enter your science score"))
    grade=result+result1+result2+result3+result4
    print("The total is " +str(grade))
    avarage=int(grade/5) 
    print("your avarage is " +str(avarage))
    l=grade/5
    if l>=90:
      print ("you have a A")
    elif l<= 89 and l> 33:
      print("you have a B")
    else:
      print("you failed")

  elif choise==5:
    break

  
  
  
  
  
  
  
  