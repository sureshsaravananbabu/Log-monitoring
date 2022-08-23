import os
import json
from logs.redis import RedisClient
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class MonitorConsumer(AsyncWebsocketConsumer):
    path="/Users/suresh/Desktop/logs/log.txt"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis=RedisClient()

    @sync_to_async
    def addToRedisDB(self,curr_modifiedtime):
        last_modifieldtime=self.redis.get("modifiedTime")
        logfile=self.redis.get("logFile")
        file_pointer=self.redis.get("filePointer")

        if last_modifieldtime:
            file_pointer=json.loads(file_pointer)
            last_modifieldtime=json.loads(last_modifieldtime)
            logfile=json.loads(logfile)
            fp=open(MonitorConsumer.path)
            fp.seek(0, 2)
            if file_pointer>fp.tell()+1:
                logfile,file_pointer=self.read_data(MonitorConsumer.path,0)
                self.redis.set("modifiedTime",json.dumps(curr_modifiedtime))
                self.redis.set("logFile",json.dumps(logfile))
                self.redis.set("filePointer",json.dumps(file_pointer))
        else:
            print("settings")
            logfile,file_pointer=self.read_data(MonitorConsumer.path,0)  
            self.redis.set("modifiedTime",json.dumps(curr_modifiedtime))
            self.redis.set("logFile",json.dumps(logfile))
            self.redis.set("filePointer",json.dumps(file_pointer))
    
        return logfile

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'monitor_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(self.room_group_name)
        ti_modified = os.path.getmtime(MonitorConsumer.path)
        data=await self.addToRedisDB(ti_modified)

        
        await self.send(text_data=json.dumps({
            'message': data
        }))



    async def disconnect(self, close_code):
    
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'monitor_logs',
                'message': message
            }
        )

    async def monitor_logs(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    def read_data(self,file_name,file_pointer):
        last_lines=[]

        def read_chunk(file_obj,chunk_size=5000):

            while True:
                data=file_obj.read(chunk_size)
                if not data:
                    break
                yield data

        fp=open(file_name)
        fp.seek(file_pointer)
        data_left_over=None

        for chunk in read_chunk(fp):

            if data_left_over:
                current_chunk=data_left_over+chunk
            else:
                current_chunk=chunk

            lines=current_chunk.splitlines()

            if current_chunk.endswith("\n"):
                data_left_over = None
            else:
                data_left_over = lines.pop()

            for line in lines:
                if len(last_lines)>9:
                    last_lines.pop(0)
                last_lines.append(line)
                
        if data_left_over:
            lines=data_left_over.splitlines()
            for line in lines:
                if len(last_lines)>9:
                    last_lines.pop(0)
                last_lines.append(line)

        file_pointer=fp.tell()+1

        return last_lines,file_pointer