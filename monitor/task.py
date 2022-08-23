import json
import os
from sys import path
from celery import shared_task
from channels.layers import get_channel_layer
import asyncio
from logs.redis import RedisClient

@shared_task
def send_notification(file_name):
    db=RedisClient()
    last_modifieldtime=db.get("modifiedTime")
    logfile=db.get("logFile")
    file_pointer=db.get("filePointer")

    if last_modifieldtime:
        file_pointer=json.loads(file_pointer)
        last_modifieldtime=json.loads(last_modifieldtime)
        logfile=json.loads(logfile)

        time_modified = os.path.getmtime(file_name)
        if time_modified!=last_modifieldtime:
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

            for line in last_lines:
                if len(logfile)>9:
                    logfile.pop(0)
                logfile.append(line)

            file_pointer=fp.tell()+1

            db.set("modifiedTime",json.dumps(time_modified))
            db.set("logFile",json.dumps(logfile))
            db.set("filePointer",json.dumps(file_pointer))

            channel_layer = get_channel_layer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if last_lines:
                loop.run_until_complete(channel_layer.group_send(
                        "monitor_logs",
                        {
                            'type': 'monitor_logs',
                            'message': last_lines
                        }
                    ))