import sys
import os
import random
import socket
import requests
import time
import re
import signal
from markov import *


class Bot(object):
    
    def __init__(self):  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)
        self.participants = set()
        self.markov = Markov()
        if os.path.exists("markov_data2.txt"):
            with open("markov_data2.txt", "r") as f:
                self.markov.markov = eval(f.read())
        
        self.running = True
    
    
    def exit(self, signum, _):
        self.running = False
        print("participants", self.participants)
        self.save()
        
    
    def save(self):
        with open("markov_data2.txt", "w") as f:
            f.write(repr(self.markov.markov))
        
        
    def run(self):
        step = 0
        while self.running:
            data = self.get_text()
            if data:
                print(data)
                if data.startswith("PING"):
                    pong = "PONG {}\n".format(data.split()[1])
                    self.sock.send(pong.encode("utf-8")) 
                
                m = re.match(r":(.+)!.+PRIVMSG #(.+) :(.*)", data)
                if m:
                    sender = m.group(1)
                    dest = m.group(2)
                    msg = m.group(3)
                    
                    if sender != self.pseudo:
                        if sender not in self.participants:
                            self.participants.add(sender)
                        
                        tokens = [tok if tok not in self.participants else "{name}" for tok in tokenize(msg)]
                        for i in range(len(tokens) - 1): 
                            self.markov.feed(tuple(tokens[max(0,i-1):max(1,i+1)]), tokens[i+1])
                            self.save()
                        
                        if self.pseudo in msg:
                            # Answer
                            self.speak()
                            
                        
                m = re.match(r":(.+)!.+JOIN #(.+)", data)
                if m:
                    sender = m.group(1)
                    dest = m.group(2)
                    if sender != self.pseudo:
                        if sender not in self.participants:
                            self.participants.add(sender)
                        if len(self.markov.markov) > 0 and random.random() < 0.3:
                            self.speak()
                    
            time.sleep(2)
    

    def speak(self):
        answer = self.markov.generate2()
        while "{name}" in answer:
            answer.replace("{name}", random.choice(list(participants)))
        while "{num}" in answer:
            answer.replace("{num}", random.choice([1, 2, 3, 5, 7, 9]))
        self.send(answer)
    
    
    def send(self, msg):
        self.sock.send(f"PRIVMSG {self.channel} :{msg}\n".encode("utf-8"))


    def connect(self, server, channel, pseudo):
        self.channel = channel
        self.server = server
        self.pseudo = pseudo
        
        print("connecting to:" + self.server)
        
        messages = [f"NICK {pseudo}\n",
                    f"USER {pseudo} 0 * : un bot apprenant\n",
                    f"JOIN {channel}\n"]
        self.sock.connect((server, 6667))
        for m in messages:
            self.sock.send(m.encode('utf-8'))
    
    
    def get_text(self):
        try:
            data = self.sock.recv(2048).decode('utf-8')
        except:
            self.send("[WARNING] Données invalides détectées")
            data = ""
        return data
    
    
    

if __name__ == "__main__":
    chan = "#labaleine"
    serv = "irc.freenode.net"
    nick = "marco2"
    
    b = Bot()
    b.connect(serv, chan, nick)
    b.run()
    print("Program exited gracefully")
    
