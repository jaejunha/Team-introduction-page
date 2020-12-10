import random
import requests
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

URL_INSTAGRAM = "https://www.instagram.com/"
URL_NAVER = "https://blog.naver.com/PostList.nhn?blogId="

CONST_PORT = 810
CONST_8KB = 8192 

dic_favorite = None
list_name = None

def getMembers():
	global list_name

	list_name = []	
	file = open("_favorite/members.txt", "r", encoding = "utf-8")
	for line in file.readlines():
		list_name.append(line.strip())

	print(list_name)

def getNaverProfile(name, user):
	img = None

	url = URL_NAVER + user
	print("Download image from: " + url)
	res = requests.get(url)
	list_line = res.text.split("\n")
	for line in list_line:
		if "og:image" in line:
			img = line.split('"')[3]
			close = urllib.request.urlopen(img).read()
			file_img = open("_favorite/" + name + ".jpg", "wb")
			file_img.write(close)
			file_img.close()
			break
	return img

def getInstaProfile(name, user):
	img = None

	url = URL_INSTAGRAM + user
	file = open("session.txt", "r", encoding = "utf-8")
	session = file.readlines()[0].strip()
	cookies = {"sessionid": session}
	print("Download image from: " + url)
	res = requests.get(url, cookies = cookies)
	list_line = res.text.split("\n")
	for line in list_line:
		if "og:image" in line:
			img = line.split('"')[3]
			close = urllib.request.urlopen(img).read()
			file_img = open("_favorite/" + name + ".png", "wb")
			file_img.write(close)
			file_img.close()
			break
	return img

def updateProfile():
	global dic_favorite
	dic_favorite = {}

	file = open("_favorite/naver.txt", "r", encoding = "utf-8")
	for line in file.readlines():
		if "," in line:
			list_ele = line.strip().split(",")
			name = list_ele[0].strip()
			user = list_ele[1].strip()
			img = getNaverProfile(name, user)
	file.close()

	file = open("_favorite/instagram.txt", "r", encoding = "utf-8")
	for line in file.readlines():
		if "," in line:
			list_ele = line.strip().split(",")
			name = list_ele[0].strip()
			user = list_ele[1].strip()
			img = getInstaProfile(name, user)

			dic_favorite[name] = {"user": user, "img": img}
	file.close()

def checkImage(path):
	return ".png" in path or ".jpg" in path or ".gif" in path or ".ico" in path

def getContent(path):
	str = ""
	file = open(path, "r", encoding = "utf-8")
	for i, line in enumerate(file.readlines()):
		if i == 0:
			str += "<h1>%s</h1>" % line.split(":")[1].strip()
		elif i == 1:
			continue
		else:
			str += line

	return str


class HandlerHTTP(BaseHTTPRequestHandler):
	def setup(self):
		BaseHTTPRequestHandler.setup(self)
		self.request.settimeout(1)

	def _set_headers(self, code, type = "html"):
		self.send_response(code)
		if type == "html":
			self.send_header('Content-type', 'text/html')
		else:
			self.send_header('Content-type', 'image/' + type)
		self.end_headers()
	
	def _redirect(self, url):
		self.send_response(302)
		self.send_header("Location", url)
		self.end_headers()
		
	def do_GET(self):
		access = False
		if self.path == "/":
			access = True
			self.path = "intro.html"
		elif self.path == "/index":
			access = True
			self.path = "index.html"
		else:
			self.path = "." + self.path

		try:
			if checkImage(self.path):
				access = True
				self._set_headers(200, self.path.split(".")[-1])
				file = open(self.path, "rb")
				data = file.read(CONST_8KB)
				self.wfile.write(data)
				while data:
					data = file.read(CONST_8KB)
					self.wfile.write(data)
			else:
				if access is False:
					raise FileNotFoundError

				self._set_headers(200, "html")
				file = open(self.path, "r", encoding = "utf-8")
				str_data = ""
				for line in file.readlines():
					if ":)" in line:
						start = line.find(":)")
						end = line.find("&")
						path = "_post/" + line[start + 2: end] + ".txt"
						content = getContent(path)
						line = line.replace(line[start: end + 1], content)
					if ";)" in line:
						start = line.find(";)")
						end = line.find("&")	
						list_name = list(dic_favorite.keys())
						random.shuffle(list_name)
						content = ""
						for name in list_name:
							content += '<div style="display:inline-block;clear:both;padding:5px;"><center><a href="https://www.instagram.com/' + dic_favorite[name]["user"] + '" target="_blank">'
							img = dic_favorite[name]["img"]
							if img is not None:
								content += '<img class="img_favorite" src="_favorite/' + name + '.png"/><br>'
							else:
								content += '<img class="img_favorite" src="" /><br>'
							content += name
							content += "</center></a></div>"
						line = line.replace(line[start: end + 1], content)
							
						
					str_data += line
				self.wfile.write(str_data.encode())

			file.close()

		except FileNotFoundError:
			self._set_headers(404)
			self.wfile.write(bytes(b"404 Not Found"))		
		except Exception as e:
			print(e)

if __name__ == "__main__":	

	getMembers()
	updateProfile()
	server_http = HTTPServer(("", CONST_PORT), HandlerHTTP)
	server_http.serve_forever()
