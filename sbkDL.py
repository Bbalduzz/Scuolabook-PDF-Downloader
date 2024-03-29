import requests, json, re, fitz
from dataclasses import dataclass
from typing import List, Union

raw_url = input('Enter the book url: \n')

with open('cookies.txt', 'r') as f: auth = f.readline()
HEADERS = {'Cookie':auth}

@dataclass
class Book:
	title:str
	author:str
	isbn:str
	pages:str
	toc: List[List[Union[int, str]]]
	identifier: str

def convert_toc(toc_list):
    toc_dict = {}
    result = []
    for item in toc_list:
        title = item['title']
        page = int(item['page'])
        for prev_title, prev_layer in toc_dict.items():
            if title.startswith(prev_title):
                layer = prev_layer + 1
                title = title.removeprefix(f'{prev_title} - ')
                break
        else: layer = 1
        toc_dict[title] = layer
        result.append([layer, title, page])
    return result

def book_info():
	req = requests.get(raw_url, headers=HEADERS).text
	book_metadata = re.findall('(?<=books:)(.*)(?=)', req)[0].removesuffix(',')
	book_metadata = json.loads(book_metadata)
	raw_toc = book_metadata[0]['spine']['sections']
	toc = convert_toc(raw_toc)
	return Book(book_metadata[0]['ws_title'], book_metadata[0]['ws_author'], book_metadata[0]['ws_isbn'], book_metadata[0]['ws_num_pages'], toc, book_metadata[0]['ws_book_id'])

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f"\r[+] Downloading book... |{bar}| {percent:.2f}% {progress}/{total}", end="\r")

book = book_info()
pages_per_req = [500]
def div(n):
	r = n-500
	pages_per_req.append(r)
	if r > 500:
		div(r)

def downloadbook():
	doc = fitz.Document()
	page_number = int(book.pages)
	pages = []
	if page_number > 500: # 414 Request-URI Too Large
		div(page_number)
		for n, number_of_pages in enumerate(pages_per_req):
			prev_elem = pages_per_req[n-1]
			if prev_elem == pages_per_req[-1]: prev_elem = 1
			attachment = [f'pages[]={n}&' for n in range(prev_elem, number_of_pages+prev_elem)]
			pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book.identifier}/pages?{"".join(attachment)}', headers=HEADERS).json()['pages'].values()
			pages.extend(list(pages_req))
	else:
		attachment = [f'pages[]={n}&' for n in range(1, int(book.pages))] 
		pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book.identifier}/pages?{"".join(attachment)}', headers=HEADERS).json()['pages'].values()
		pages.extend(list(pages_req))
	progress_bar(0, book.pages)
	for n,page in enumerate(pages):
		page_data = requests.get(page, headers=HEADERS).content
		page_doc = fitz.open(stream=page_data, filetype="jpg")
		pdfbytes = page_doc.convert_to_pdf()
		doc.insert_pdf(fitz.open("pdf",pdfbytes))
		progress_bar(n, book.pages)
	doc.set_toc(book.toc)
	doc.save(f'{book.title}.pdf')

print(f'''
[+] Book Found:
	- title: {book.title}
	- author: {book.author}
	- isbn: {book.isbn}
	- pages: {book.pages}
''')
downloadbook()
