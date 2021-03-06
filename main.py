import json
import requests
import pandas as pd
import threading
import time

StartTime=time.time()

AMOUNT_MIN = 1
INTERVAL_IN_SECONDS = 600

class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()


def getUnstakes(amount, timestamp):
    query = """
    {
        unstakes(orderBy:timestamp orderDirection: desc, where:{amount_gte:%d, timestamp_gte:%d}){
          id
          amount
          timestamp
          transaction{from to}
        }
    }
    """ % (amount, timestamp)
    request = requests.post('https://api.thegraph.com/subgraphs/name/drondin/olympus-graph', json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def action():
    timestamp = time.time() - INTERVAL_IN_SECONDS - 20
    unstakes_data = getUnstakes(AMOUNT_MIN, timestamp)
    unstakes_data = unstakes_data['data']['unstakes']
    print(time.time())
    df = pd.DataFrame(unstakes_data)
    file = open('res.txt', 'w')
    file.write(df.to_string())
if __name__== "__main__":
    action()
    inter = setInterval(INTERVAL_IN_SECONDS, action)
