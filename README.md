# gatito
Lightweight and portable netcat alternative for computers without internet
## Quick usage

```
gatito.py -t 192.168.1.100 -p 7777 -l -c # command shell
Example gatito.py -t 192.168.1.100 -p 7777 -l -u=test.txt # upload a file
Example gatito.py -t 192.168.1.100 -p 7777 -l -e="cat /etc/passwd" # execute command
Example echo 'abc' | ./gatito.py -t 192.168.1.100 -p 7777 # echo text to server port 123
Example gatito.py -t 192.168.1.100 -p 7777 # connect to server
```
