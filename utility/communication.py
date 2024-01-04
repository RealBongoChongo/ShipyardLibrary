import socketio
import random
import asyncio
from . import jsonhandler
import json
from threading import Thread

class WebsocketClient(socketio.Client):
    def __init__(self):
        super().__init__(
            logger=True, 
            reconnection_attempts=10
        )

        self.callbackDictionary = {}

    def invoke_callback(self, data):
        self.callbackDictionary[data["processID"]](data["data"])
        self.callbackDictionary.pop(data["processID"])
        
    def on_connection(self):
        print("Connected")

    def server_response(self, data):
        print(data)

    def ping_packet(self):
        while True:
            asyncio.run(asyncio.sleep(10))
            self.emit("ping_packet", "Ping", "/")

    def getData(self, data, callback):
        stringProcessID = str(random.randrange(100000000,999999999))

        self.callbackDictionary[stringProcessID] = callback

        self.emit("requestData", {"data": data, "processID": stringProcessID}, "/")

    def returnData(self, data):
        with open("json/library.json", "r") as f:
            jsonData = json.load(f)

        self.send({"data": jsonData, "processID": data["processID"]}, "/")

    def start(self):
        def start_task():
            self.on("connect", self.on_connection, "/")
            self.on("heartbeat", self.server_response, "/")
            self.on("callbackResponse", self.invoke_callback, "/")
            self.on("returnData", self.returnData, "/")
            #Thread(target=self.ping_packet).start()
            self.connect("https://bank.federationfleet.xyz", namespaces=["/"])
            self.wait()
        
        Thread(target=start_task).start()