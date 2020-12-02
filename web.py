from http.server import HTTPServer, BaseHTTPRequestHandler

CONST_PORT = 810

CONST_8KB = 8192 

def checkImage(path):
	return ".png" in path or ".jpg" in path or ".gif" in path or ".ico" in path

class HandlerHTTP(BaseHTTPRequestHandler):
	def setup(self):
		BaseHTTPRequestHandler.setup(self)

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
			self.path = "index.html"
		else:
			self.path = "." + self.path

		try:
			if checkImage(self.path):
				self._set_headers(200, self.path.split(".")[-1])
				file = open(self.path, "rb")
				sum_data = b""
				while True:
					data = file.read(CONST_8KB)
					sum_data += data
					if data == b"":
						break
				self.wfile.write(sum_data)
			else:
				self._set_headers(200, "html")
				file = open(self.path, "r", encoding = "utf-8")
				str_data = ""
				for line in file.readlines():
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
