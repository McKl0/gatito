# gatito
Lightweight and portable netcat alternative for computers without direct internet access

I do not consent to this code being used maliciously

This code has been made solely for academic purposes and penetration testing environments
## Quick usage
### command shell
```
gatito.py -t 192.168.1.100 -p 7777 -l -c 
```
### Upload a file
```
gatito.py -t 192.168.1.100 -p 7777 -l -u=test.txt
```
### Execute command
```
gatito.py -t 192.168.1.100 -p 7777 -l -e="cat /etc/passwd"
```
### Echo text to server port 123
```
echo 'abc' | ./gatito.py -t 192.168.1.100 -p 7777
```
### Connect to server
```
gatito.py -t 192.168.1.100 -p 7777
```
