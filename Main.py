from Frontend.GUI import (
GraphicalUserInterface,
SetAssistanceStatus,
ShowTextToScreen,
SetMicrophoneStatus,
TempDirectoryPath, AnswerModifier, QueryModifier, GetMicrophoneStatus, GetAssistanceStatus )
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars=dotenv_values(".env")
Username=env_vars.get("Username")
Assistantname=env_vars.get("Assistantname")
DefaultMessage=f'''{Username}:Hello {Assistantname},How are you?
{Assistantname}:Welcome{Username},I am doing well. How may i help you?'''
subprocesses=[]
Functions=["open","close","play","system","content","google search","youtube search"]


def ShowDefaultChatifNoChats():
    File=open(r'Data\ChatLog.json','r',encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'),'w',encoding='utf-8')as file:
            file.write("")

        with open(TempDirectoryPath('Responses.data'),'w',encoding='utf-8')as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json','r',encoding='utf-8') as file:
        content = file.read().strip()
        if not content:   # if file is empty
            return []     # return empty chat log
        return json.loads(content)


def ChatLogIntegration():
    json_data=ReadChatLogJson()
    formatted_Chatlog=""
    for entry in json_data:
        if entry["role"]=="user":
               formatted_Chatlog+=f"User:{entry['content']}\n"

        elif entry["role"]=="assistant":
             formatted_Chatlog+=f"Assistant:{entry['content']}\n"
    formatted_Chatlog=formatted_Chatlog.replace("User",Username+"")
    formatted_Chatlog=formatted_Chatlog.replace("Assistant",Assistantname+"")
    
    with open(TempDirectoryPath('Database.data'),'w',encoding='utf-8')as file:
            file.write(AnswerModifier(formatted_Chatlog))

def ShowChatsOnGUI():
    File=open(TempDirectoryPath('Database.data'),'r',encoding='utf-8')
    Data=File.read()

    if len(str(Data))>0:
         lines=Data.split('\n')
         result='\n'.join(lines)
         File.close()
         File=open(TempDirectoryPath('Responses.data'),'w',encoding='utf-8')
         File.write(result)
         File.close()


def InitialExecution():
     SetMicrophoneStatus("False")
     ShowTextToScreen("")
     ShowDefaultChatifNoChats()
     ChatLogIntegration()
     ShowChatsOnGUI()

InitialExecution()

def MainExecution():
     TaskExecution=False
     ImageExecution=False
     ImageGenrationQuery=""

     SetAssistanceStatus("Listening...")
     Query=SpeechRecognition()
     ShowTextToScreen(f"{Username}:{Query}")
     SetAssistanceStatus("Thinking...")
     Decision=FirstLayerDMM(Query)

     print("")
     print(f"Decision: {Decision} ")
     print("")

     G=any([i for i in Decision if i.startswith("general")])
     R=any([i for i in Decision if i.startswith("realtime")])

     Merged_query="and".join(
          ["".join(i.split()[1:])for i in Decision if i.startswith("general") or i.startswith("realtime")]
     )

     for queries in Decision:
          if "generate " in queries:
               ImageGenrationQuery=str(queries)
               ImageExecution=True
               break  

     for queries in Decision:
          if TaskExecution==False:
               if any(queries.startswith(func) for func in Functions):
                    run(Automation(list(Decision)))
                    TaskExecution=True

     
     if ImageExecution== True:
          
          with open(r"Frontend\Files\ImageGenration.data",'w')as file:
               file.write(f"{ImageGenrationQuery},True")


          try:
               p1=subprocess.Popen(['python',r'Backend\ImageGenration.py'],
                                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE, shell=False)
               
               subprocesses.append(p1)
          except Exception as e:
               print(f"Error starting ImageGenration.py:{e}")


     if G and R or R:
          SetAssistanceStatus("Searching...")
          Answer=RealtimeSearchEngine(QueryModifier(Merged_query))
          ShowTextToScreen(f"{Assistantname}:{Answer}")
          SetAssistanceStatus("Answering...")
          TextToSpeech(Answer)
          return True
     
     else:
          for Queries in Decision:
               
               if "general"in Queries:
                    SetAssistanceStatus("Thinking...")
                    QueryFinal=Queries.replace("general","")
                    Answer=ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}:{Answer}")
                    SetAssistanceStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
               
               elif "realtime"in Queries:
                    SetAssistanceStatus("Searching...")
                    QueryFinal=Queries.replace("realtime","")
                    Answer=RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAssistanceStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
               
               elif "exit" in Queries:
                    QueryFinal="Okey Bye!"
                    Answer=ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}:{Answer}")
                    SetAssistanceStatus("Answering...")
                    TextToSpeech(Answer)
                    SetAssistanceStatus("Answering...")
                    os._exit(1)


def FirstThread():
     while True:
          
          CurrentStatus=GetMicrophoneStatus()

          if CurrentStatus=="True":
               MainExecution()

          else:
                AIstatus=GetAssistanceStatus()

                if "Available..." in AIstatus:
                    sleep(0.1)

                else:
                    SetAssistanceStatus("Available...")

def SecondThread():
     
     GraphicalUserInterface()

if __name__=="__main__":
     thread2=threading.Thread(target=FirstThread,daemon=True)
     thread2.start()
     SecondThread()
                    