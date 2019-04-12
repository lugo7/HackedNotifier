import os.path
import requests
from bs4 import BeautifulSoup
import json
import smtplib
import pickle
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from string import Template
from smtplib import SMTP_SSL as SMTP #always uses a secure connection.

###############################################################################
#MAKE SURE A VPN IS ENABLED WHEN YOU LAUNCH THIS SCRIPT.

#Certain webpages require javascript, and cookies enabled. (script doesn't account for this yet).
#If scraping doesn't work, copy and paste the emails into a file named 'emails.txt'.

#Script requires you to run it multiple times, it will perform the correct action based on what files are present in root directory.
###############################################################################

def getWebContent(website):
    page=requests.get(website)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(soup)
    messageList=soup.find_all('a') #returns a list
    return messageList

def dictify(parsedContent):
  tempDict={}
  for item in parsedContent:
    #Otherwise split the string on the first space, making the latter section the definition.
    a,b=item.split(":",1)
    tempDict.update({a:b})
  return(tempDict)

def saveFile(emailDict):
    with open('emails2.txt', 'w') as file:
        file.write(json.dumps(emailDict))

def dictList(file):
    #Parses a text file into a list, and strips newlines, and NULL entries.
    with open(file,'r') as doc:
        wordsList=doc.read().splitlines()
    temp=list(map(lambda each: each.strip('\n'),wordsList))
    temp=list(map(lambda each: each.strip(""),temp))
    temp=list(map(lambda each: each.strip(),temp))
    return(temp)

def getEmail(emailDict):
    tempKey=[]
    tempValue=[]
    for key, value in emailDict.items():
        tempKey.append(key)
        tempValue.append(value)
    z=zip(tempKey,tempValue)
    return(z)

def nameSplit(emailAddress):
    y=emailAddress.split('@',1)
    return(y[0])

def createChunks(emailList,passwordList):
    emailChunks = [emailList[x:x+500] for x in range(0, len(emailList), 500)]
    passwordChunks = [passwordList[x:x+500] for x in range(0, len(passwordList), 500)]
    if not os.path.exists('chunkFiles'):
        os.makedirs('chunkFiles')
        for item in range(len(emailChunks)):
            with open("chunkFiles/emailChunks{num}.txt".format(num=item),'wb') as f:
                pickle.dump(emailChunks[item], f)
                f.close()
        for item in range(len(passwordChunks)):
            with open("chunkFiles/passwordChunks{num}.txt".format(num=item),'wb') as f:
                pickle.dump(passwordChunks[item], f)
                f.close()
    else:
        pass

def loadChunks():
    if not os.path.exists('chunkChecker.txt'):
        x=0
        with open("chunkChecker.txt", 'w') as f:
            f.write(str(x))
            f.close()
    with open("chunkChecker.txt", 'r') as f:
        placemark=f.read()
        placemark=placemark.strip('\n')
        print(placemark)
        f.close()
    with open("chunkChecker.txt", 'w') as f:
        k=int(placemark)
        if k<=14:
            k=k+1
        f.write(str(k))
        f.close()
    with open("chunkFiles/emailChunks{num}.txt".format(num=placemark),'rb') as f:
        y=pickle.load(f)
        f.close()
    with open("chunkFiles/passwordChunks{num}.txt".format(num=placemark),'rb') as f:
        p=pickle.load(f)
        f.close()
    c=zip(y,p)
    return(c)

def connectSMTP(emailUser,emailPass):
    try:
        s=smtplib.SMTP() #Input which Email server you wish to connect to, as well as the port number.#####################
        s.set_debuglevel(True)
        s.starttls()
        s.ehlo()
        s.login(emailUser, emailPass)
    except exception as e:
        print('Could not log in')
        print(e)
    print("log in successful")
    return(s)

def test_conn_open(conn):
    try:
        status = conn.noop()[0]
    except:  # smtplib.SMTPServerDisconnected
        status = -1
    return True if status == 250 else False

def sendEmail():
    emailUser=str() #Input the Email Address you wish to use.#########################
    emailPass=str() #Input the password for your Email Address.######################
    with open("emails2.txt", 'r') as doc:
        emailDict=json.load(doc)
    with open("message.txt", 'r',encoding='utf-8') as text:
        template=Template(text.read())
        text.close()
    z=getEmail(emailDict)
    emailList,passwordList=zip(*z)
    emailList=list(emailList)
    passwordList=list(passwordList)
    createChunks(emailList,passwordList)
    c=loadChunks()
    sendList,pList=zip(*c)
    sendList=list(sendList)
    pList=list(pList)
    try:
        s=connectSMTP(emailUser,emailPass)
        for i in range(len(sendList)):
            if not test_conn_open(s):
                s=connectSMTP(emailUser,emailPass)
            print('Preparing message: {b}'.format(b=i))
            message=template.safe_substitute(USERNAME=nameSplit(sendList[i]),EMAIL=sendList[i],PASSWORD=pList[i])
            msg=MIMEMultipart()
            msg['From']=emailUser
            msg['Subject']="Password notice"
            msg.attach(MIMEText(message, 'plain'))
            msg['To']=sendList[i]
            s.sendmail(emailUser,sendList[i],msg.as_string())
            print('Message sent successfully: {b}'.format(b=i))
            time.sleep(5)
            print('\n \n')
        s.quit()
        print("Chunk sent successfully")
    except (SMTPSenderRefused, socket.error, OSError, IOError, SMTPAuthenticationError) as e:
        print(e)

if __name__=="__main__":
    #If no email files exist, web scrape items in siteList for email Addresses.
    if(os.path.isfile('emails.txt')!=True):
        siteList=[] #insert the specific webpages that you wish to scrape into this list.######################
        emailDict={}
        for i,site in enumerate(siteList):
            print(siteList[i])
            messageList=getWebContent(siteList[i])
            if len(messageList)==0:
                print("messageList is empty")
            parsedContent=[x for x in workingList if "@" in x]
            parsedContent=list(map(lambda each: each.strip('\n'),parsedContent))
            parsedContent=list(map(lambda each: each.strip(),parsedContent))
            emailDict.update(dictify(parsedContent))
        saveFile(emailDict)

    #If a file of email addresses exists, turn meaningless string into a nice dictionary.
    elif(os.path.isfile('emails2.txt')!=True): #check if the text file exists.
        workingList = dictList('emails.txt') #Creates a string from a textfile
        workingList=list(filter(None,workingList)) #removes empty list entries
        parsedContent=[x for x in workingList if "@" in x]
        newDict=dictify(parsedContent) #Takes in list, returns dictionary
        saveFile(newDict)

    #If email Dictionary exists, send out warning message to all addresses.
    elif(os.path.isfile('emails2.txt')==True):
        sendEmail()
