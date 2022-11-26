import requests, os, shutil, json
from natsort import natsorted
from PIL import Image
from bs4 import BeautifulSoup
import re
from PyPDF2 import PdfFileReader, PdfFileWriter

try: os.mkdir('pages')
except: pass

raw_url = input('Enter the book url: \n')
book_id = raw_url.split('/')[4]

with open('cookies.txt', 'r') as f: auth = f.readline()
HEADERS = {'Cookie':auth}
npages = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/plus', headers=HEADERS).json()[-1]['page']

def book_info():
	req = requests.get(raw_url, headers=HEADERS).content
	soup = BeautifulSoup(req, 'html.parser')
	scripts = soup.select('script')[5].text
	book_metadata = re.findall('(?<=books:)(.*)(?=)',scripts)[0].removesuffix(',')
	book_metadata = json.loads(book_metadata)
	toc = book_metadata[0]['spine']['sections']
	return book_metadata[0]['ws_title'], book_metadata[0]['ws_author'], book_metadata[0]['ws_isbn'], book_metadata[0]['ws_num_pages'], toc

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f'\r [+] Downloading book... |{bar}| {percent:.2f}%', end='\r')

book_infos = book_info()

def dl():
	attachment = [f'pages[]={n}&' for n in range(1, int(npages)+1)]
	params = ''.join(attachment)
	pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/pages?{params}', headers=HEADERS).json()

	progress_bar(0, npages)
	for n in range(1, int(npages)+1):
		page_url = pages_req['pages'][str(n)]
		page_data = requests.get(page_url, headers=HEADERS).content
		with open(f'pages/page{n}.png', 'wb') as image:
			image.write(page_data)
		progress_bar(n+1, npages)
		
def add_toc(toc):
	print('\n[+] Applying ToC',end='\n')
	reader = PdfFileReader(f"{book_infos[0]}.pdf")
	writer = PdfFileWriter()
	n = reader.getNumPages()
	for i in range(n):
		writer.addPage(reader.getPage(i))
	for c in toc:
		page_index = int(c['page'])
		book_mark = c['title']
		writer.addBookmark(book_mark, page_index-1, parent=None)
		with open(f"{book_infos[0].capitalize()}.pdf", "wb") as fp:
			writer.write(fp)

def create_pdf():
	dl()
	file_names = os.listdir('pages')
	file_names = natsorted(file_names)
	pdfimages = [Image.open(f'pages/{f}') for f in file_names]
	pdf_path = book_infos[0] + '.pdf'
	pdfimages[0].save(pdf_path, "PDF" , resolution=100.0, save_all=True, append_images=pdfimages[1:])
	shutil.rmtree('pages')
	add_toc(book_infos[4])
	print('Done :)')

print(f'''
[+] Book Found:
	- title: {book_infos[0]}
	- author: {book_infos[1]}
	- isbn: {book_infos[2]}
	- pages: {book_infos[3]}
''')
create_pdf()
