import requests
import json
import random
from html.parser import HTMLParser

class JokeProvider(object):
    
    def getJoke(self): 
        raise NotImplementedError()

class ChuckJokeProvider(JokeProvider):
    def getJoke(self):
        r = requests.get("http://api.icndb.com/jokes/random1http://api.icndb.com/jokes/random?firstName=Peter&lastName=Hofmann")
        return HTMLParser().unescape(r.json()["value"]["joke"])


class OfflineJoker(JokeProvider):
    
    def __init__(self, fileName):
        self._fileName = fileName
        
    def getRandomJoke(self, jokes):
        randomIndex = random.randint(0, len(jokes) - 1)
        joke = jokes[randomIndex]
        body = jokes[randomIndex]["body"]
        return body
    
    def getJoke(self):
        json_data=open(self._fileName).read()
        jokes = json.loads(json_data)
        
        joke = self.getRandomJoke(jokes)
        while(len(joke) == 0 or len(joke) > 200):
            joke = self.getRandomJoke(jokes)
        return joke

class LineJoker(JokeProvider):
    def __init__(self, fileName):
        self._fileName = fileName
        
    def getRandomJoke(self, jokes):
        print(len(jokes))
        randomIndex = random.randint(0, len(jokes) - 1)
        joke = jokes[randomIndex]
        return joke
    
    def getJoke(self):
        f = open(self._fileName, "r")
        jokes = f.readlines()
        f.close()
        
        joke = self.getRandomJoke(jokes)
        return joke

class RandomJoker(JokeProvider):
    def __init__(self):
        self._jokers = []
    
    def add(self, jokeProvider):
        self._jokers.append(jokeProvider)
    
    def getJoke(self):
        randomIndex = random.randint(0, len(self._jokers) - 1)
        return self._jokers[randomIndex].getJoke()

