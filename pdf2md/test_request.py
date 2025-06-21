import requests

url = "http://127.0.0.1:8000/uploadandconvert"
pdf = "test_pdfs/49e3023b785924a7159ee756c546ac2ec523e8ea.pdf"

files = {'file': open(pdf, 'rb')}
response = requests.post(url, files=files)
print(response.json())