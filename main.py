from http.server import BaseHTTPRequestHandler,HTTPServer
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

host = "localhost"
port = 3001

def generateEmail(attackerAddress, attackerUsedURL, fromEmailAddress, toEmailAddress):
	message = "Hello There...\nSomeone is trying to attack your server\nIntrusion Detected on your server "+ str(readCount()) +"Times\nAttacker IP: "+attackerAddress+"\nString used in URL by Attacker: "+attackerUsedURL+"\nPlease check server logs immidiately for more details\nThanks"
	email = MIMEMultipart()
	email['From'] = fromEmailAddress
	email['To'] = toEmailAddress
	email['Subject'] = "Alert !!! Intrusion Detected: "+ str(readCount())
	email.attach(MIMEText(message, 'plain'))
	return email.as_string()

def readCount():
	count = 0
	with open("count.txt", "r") as countFromFile:
		c = countFromFile.read()
		if c:
			nums = map(int, c)
			for i in nums:
				count = (count*10) + i
	return count

def increaseCount():
	try:
		count = readCount()
		with open("count.txt", "w") as countFromFile:
			data = countFromFile.write(str(count+1))
	except:
		with open("count.txt", "w") as countFromFile:
			data = countFromFile.write(str(1))
	return

def sendMail(attackerAddress, attackerUsedURL):
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login("email@gmail.com", "password")
	fromEmailAddress = "email@gmail.com"
	toEmailAddress = "email@gmail.com"
	email = generateEmail(attackerAddress, attackerUsedURL, fromEmailAddress, toEmailAddress)
	server.sendmail(fromEmailAddress, toEmailAddress, email)
	print("\n\n"+"Sent Email\nFrom:\t"+fromEmailAddress+"\nTo:\t"+toEmailAddress+"\nIntrusion Detected "+str(readCount())+"\n\n")

def get2Grams(payload_obj):
    payload = str(payload_obj)
    ngrams = []
    for i in range(0,len(payload)-2):
        ngrams.append(payload[i:i+2])
    return ngrams

def isMalicious(inputs):
    return True if classifier.predict([inputs]).sum() > 0 else False

class Handler(BaseHTTPRequestHandler):
	def do_GET(self):
		if isMalicious(self.path[1:]):
			increaseCount()
			sendMail(str(self.client_address[0]) + ":" +str(self.client_address[1]), self.path[1:])
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(bytes("MALICIOUS URL ENTRY", "utf8"))
		else:
			self.send_response(301)
			new_path = 'https://google.com'
			self.send_header('Location', new_path)
			self.end_headers()
		return


try:
	print("Loading Classifier...")
	classifier = pickle.load(open("tfidf_2grams_randomforest.p", "rb"))
	print("Classifier Loaded Sccussfully")
	server = HTTPServer((host, port), Handler)
	print("Started Server on " + host + ":" + str(port) + " ...")
	server.serve_forever()
except KeyboardInterrupt:
	print ('^C received, shutting down the web server')
	server.socket.close()