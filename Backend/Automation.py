from AppOpener import open as appopener
from AppOpener import close
from webbrowser import open as webopen
from pywhatkit import search,playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq

import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars=dotenv_values(".env")
GroqAPIKey=env_vars.get("GroqAPIKey")

classes=["zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk. FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
        "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe",
        "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"

client=Groq(api_key=GroqAPIKey)


professional_responses=[
"Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
 "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]


messages=[]

SystemChatBot=[{"role":"system","content":f"Hello i am {os.environ['Username']},You're a content writer .You have to write content like lette"}]

def GoogleSearch(Topic):
    search(Topic)
    return True



def content(Topic):


    def OpenNotepad(file):
        default_text_editor='notepad.exe'
        subprocess.Popen([default_text_editor,file])


    def ContentWritingAI(prompt):
        messages.append({"role":"system","content":f"{prompt}"})

        completion=client.chat.completions.create(
            model='llama3-70b-8192',
            messages=SystemChatBot+messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer=""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer+=chunk.choices[0].delta.content


            Answer=Answer.replace("</s>","")

            messages.append({"role":"assistant","content":Answer})

        return Answer
        
    Topic:str=Topic.replace("Content","")
    ContentByAI=ContentWritingAI(Topic)

    with open (rf"Data{Topic.lower().replace(' ','')}.txt","w",encoding="utf-8")as file:
        file.write(ContentByAI)
        file.close()


    OpenNotepad(rf"Data{Topic.lower().replace(' ','')}.txt")
    return True




def YouTubeSearch(Topic):
    Url4Search=f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app,sess=requests.session()):
    try:
        appopener(app,match_closest=True,output=True,throw_error=True)
        return True
    except:
        def ectract_links(html):
            if html is None:
                return[]
            
            soup=BeautifulSoup(html,'html.parser')
            links=soup.find_all('a',{'jsname':'UWckNb'})
            return[link.get('href') for link in links]
        

        def search_google(query):
            
            url=f"https://www.google.com/search?q={query}"
            headers={"User-Agent": useragent}
            responce=sess.get(url,headers=headers)

            if responce.status_code==200:
                return responce.text
            else:
                print("Failed to recive search results. ")

            return None
        
        html=search_google(app)

        if html:
            link=ectract_links(html)[0]
            webopen(link)

        return True    

def CloseApp(app):
    if "chrome" in app:
        pass

    else:
        try:
            close(app, match_closest=True, output=True,throw_error=True)
            return True

        except:
            return False

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume unmute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")  

    if command=="mute":
        mute()

    elif command=="unmute":
        unmute()  

    elif command=="volume up":
        volume_up()
    elif command=="volume down":
        volume_down()   

    return True



async def TranslateAndExecute(commands:list[str]):

    funcs=[]

    for command in commands:
        if command.startswith("open "):

            if "open it"in command:
                pass
            if "open file"==command:
                pass

            else:
                fun =asyncio.to_thread(OpenApp,command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("genral "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun =asyncio.to_thread(OpenApp,command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun =asyncio.to_thread(OpenApp,command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun =asyncio.to_thread(OpenApp,command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun =asyncio.to_thread(OpenApp,command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun =asyncio.to_thread(OpenApp,command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun =asyncio.to_thread(OpenApp,command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function Found For {command}")

        results=await asyncio.gather(*funcs)

        for result in results:
            if isinstance(result,str):
                yield result

            else:
                yield result

async def Automation(commands:list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
