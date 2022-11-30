import requests, json
from bs4 import BeautifulSoup
import re
import fitz

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
	attachment = [f'pages[]={n}&' for n in range(1, int(book_infos[3]))]
	params = ''.join(attachment)
	pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/pages?{params}', headers=HEADERS).json()

	doc = fitz.Document()
	progress_bar(0, book_infos[3])
	for n in range(1, int(book_infos[3])):
		page_url = pages_req['pages'][str(n)]
		page_data = requests.get(page_url, headers=HEADERS).content
		page_doc = fitz.open(stream=page_data, filetype="jpg")
		pdfbytes = page_doc.convert_to_pdf()
		doc.insert_pdf(fitz.open("pdf",pdfbytes))
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
