#Gmail smtp servers, as well as most other servers, have a send limit set upon them.
#A maximum of 500 messages per 24 hour rolling periods are allowed to be sent.
import json

def getEmail(emailDict):
    tempKey=[]
    tempValue=[]
    for key, value in emailDict.items():
        tempKey.append(key)
        tempValue.append(value)
    z=zip(tempKey,tempValue)
    return(z)

if __name__=="__main__":
    with open("emails2.txt", 'r') as doc:
        emailDict=json.load(doc)
    z=getEmail(emailDict)
    emailList,passwordList=zip(*z)
    chunks = [emailDict[x:x+500] for x in range(0, len(emailDict), 500)]
    print(chunks)
