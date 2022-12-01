import requests, os, shutil, json
from natsort import natsorted
from PIL import Image
from bs4 import BeautifulSoup
import re, json
import fitz
import math

raw_url = input('Enter the book url: \n')
book_id = raw_url.split('/')[4]

with open('cookies.txt', 'r') as f: auth = f.readline()
HEADERS = {'Cookie':auth}

def book_info():
	req = requests.get(raw_url, headers=HEADERS).content
	soup = BeautifulSoup(req, 'html.parser')
	scripts = soup.select('script')[5].text
	book_metadata = re.findall('(?<=books:)(.*)(?=)',scripts)[0].removesuffix(',')
	book_metadata = json.loads(book_metadata)
	raw_toc = book_metadata[0]['spine']['sections']
	toc = [[1, sec['title'], int(sec['page'])] for sec in raw_toc]
	return book_metadata[0]['ws_title'], book_metadata[0]['ws_author'], book_metadata[0]['ws_isbn'], book_metadata[0]['ws_num_pages'], toc

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f'\r[+] Downloading book... |{bar}| {percent:.2f}%', end='\r')

book_infos = book_info()

def dl():
	def get_divisions(x, n):
	    divs = [0]
	    if(x < n):
	        divs.append(-1)
	    elif (x % n == 0):
	        for i in range(n):
	            divs.append(x//n)
	    else:
	        zp = n - (x % n)
	        pp = x//n
	        for i in range(n):
	            if(i>= zp):
	            	divs.append(pp + 1)
	            else:
	                divs.append(pp)
	    return divs

	pages_url = '{'
	if int(book_infos[3]) > 518: # 414 Request-URI Too Large
		req_nums = math.ceil(int(book_infos[3]) / 518)
		upto = get_divisions(int(book_infos[3]), req_nums)
		for i,n in enumerate(upto):
			if upto[i-1] == upto[-1]:
				start = 0
				end = n
			else:
				start = upto[i-1]
				end = int(book_infos[3]) - n + upto[i-1]
			attachment = [f'pages[]={n}&' for n in range(start, end)]
			pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/pages?{"".join(attachment)}', headers=HEADERS).text
			pages_url += pages_req
	else:
		attachment = [f'pages[]={n}&' for n in range(1, int(book_infos[3]))]
		pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/pages?{"".join(attachment)}', headers=HEADERS).text
		pages_url += pages_req

	pages_url = pages_url.replace(r'}}', ',').replace(r'{"pages":{','').removesuffix(',') + '}'
	pages_url =  json.loads(pages_url)
	doc = fitz.Document()
	progress_bar(0, book_infos[3])
	for n in range(1, int(book_infos[3])):
		try:
			page_url = pages_url[str(n)]
			page_data = requests.get(page_url, headers=HEADERS).content
			page_doc = fitz.open(stream=page_data, filetype="jpg")
			pdfbytes = page_doc.convert_to_pdf()
			doc.insert_pdf(fitz.open("pdf",pdfbytes))
		except:
			doc.new_page()
		progress_bar(n+1, book_infos[3])

	doc.set_toc(book_infos[4])
	doc.save(f'{book_infos[0]}.pdf')

print(f'''
[+] Book Found:
	- title: {book_infos[0]}
	- author: {book_infos[1]}
	- isbn: {book_infos[2]}
	- pages: {book_infos[3]}
''')
dl()
