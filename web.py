from http.server import HTTPServer, BaseHTTPRequestHandler

CONST_PORT = 810

CONST_8KB = 8192 

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
		if self.path == "/":
			self.path = "intro.html"
		elif self.path == "/index":
			self.path = "index.html"
		else:
			self.path = "." + self.path

		try:
			if checkImage(self.path):
				self._set_headers(200, self.path.split(".")[-1])
				file = open(self.path, "rb")
				data = file.read(CONST_8KB)
				self.wfile.write(data)
				while data:
					data = file.read(CONST_8KB)
					self.wfile.write(data)
			else:
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
					str_data += line
				self.wfile.write(str_data.encode())

			file.close()

		except FileNotFoundError:
			self._set_headers(404)
			self.wfile.write(bytes(b"404 Not Found"))		
		except Exception as e:
			print(e)

if __name__ == "__main__":	

	server_http = HTTPServer(("", CONST_PORT), HandlerHTTP)
	server_http.serve_forever()
