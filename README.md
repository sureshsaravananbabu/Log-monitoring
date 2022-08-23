# Log-monitoring
This is similar to tail-f command


This is real time log monitoring This will retrieve the last 10 line of file effeicently</br>

It has been Build using
Python</br>
Celery</br>
Redis</br>
Django</br>
Django channels</br>


This is capable of sending the event to all the channels which has been subscribed to the group.


Explaination
Once you start the Server the websocket connect will be established between server and client it will get the last 10 lines from the file and store that in redis for the first time. If any other client come next time it has last 10 lines already stored in redis so it will fetch that and show it to user. when Any update happens to the file Then we have a scheduler which continuously monitor the file for every 2 second if any update has happend recenlty or not If it happens this will get that and send the data asynchronously 

