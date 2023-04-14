import yaml
from urllib.parse import urlparse
import sys
import time
import requests
import threading

domains = {}

def main():
    #parse yml file
    file_path = sys.argv[1]
    with open(file_path, 'r') as file:
        endpoints = yaml.safe_load(file)

    #Loops every 15 seconds until program is terminated
    while(True):
        #make requests to following endpoints, multithreading to decrease checking time
        for i in range(len(endpoints)):
            thread = threading.Thread(target=checkEndpoint, args=(endpoints[i],))
            thread.start()
        time.sleep(2)
        for k, v in domains.items():
            print("{0} has {1}% availability percentage".format(k, round((v[0] / v[1]) * 100)))
        time.sleep(15)  

def checkEndpoint(endpoint):
    url = endpoint['url']
    #parse request headers/body
    request = {}
    if "headers" in endpoint:
        request = endpoint['headers']
    if "body" in endpoint:
        request['body'] = endpoint['body']
    
    #send requests
    response = {}
    if 'method' not in endpoint or endpoint['method'] == 'GET':
        response = requests.get(url, params=request)
    elif endpoint['method'] == 'POST':
        response = requests.post(url, json=request)
    else:
        response = requests.request(endpoint['method'], url, args=request)
    
    #check if request is successful
    success = False 
    if response.status_code >= 200 and response.status_code <= 299 and (response.elapsed.microseconds / 1000) < 500:
        success = True
    
    #update stats
    global domains
    domain = urlparse(url).netloc
    if domain not in domains:
        domains[domain] = [int(success == True), 1]
    else:
        domains[domain][0] = domains[domain][0] + int(success == True)
        domains[domain][1] += 1

if __name__ == "__main__":
	main()
