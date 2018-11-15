from http.server import BaseHTTPRequestHandler,HTTPServer
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import sys

host = "localhost"
port = 3001

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
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(bytes("MALICIOUS URL ENTRY", "utf8"))
		else:
			self.send_response(301)
			new_path = '%s%s'%('https://google.com')
			self.send_header('Location', new_path)
			self.end_headers()
		return
try:
	print("Loading Classifier...")
	classifier = pickle.load(open("tfidf_2grams_randomforest.p", "rb"))
	print("Classifier Loaded Sccussfully")
	server = HTTPServer((host, port), Handler)
	print("Started Server on " + host + ":" + port + " ...")
	server.serve_forever()
except KeyboardInterrupt:
	print ('^C received, shutting down the web server')
	server.socket.close()