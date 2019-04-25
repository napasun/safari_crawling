from selenium import webdriver
import sqlite3

user = "wkzkfmxk23@gmail.com"
password = ""
conn = sqlite3.connect("book.sqlite")

browser = webdriver.PhantomJS()
browser.implicitly_wait(2)

def login(user, password):
    url_login = "https://learning.oreilly.com/accounts/login/"
    browser.get(url_login)
    
    browser.find_element_by_id("id_email").send_keys(user)
    browser.find_element_by_id("id_password1").send_keys(password)
    
    form = browser.find_element_by_css_selector("input#login[type=submit]")
    form.submit()

def get_book_link_listBysearch_page(search, page):
    url_list = "https://learning.oreilly.com/search/?query={search}&extended_publisher_data=true&highlight=true&include_assessments=false&include_case_studies=true&include_courses=true&include_orioles=true&include_playlists=true&is_academic_institution_account=false&formats=book&sort=date_added&page={page}"
    browser.get(url_list.format(search=search, page=page))
    result = []
    cards = browser.find_elements_by_css_selector("article.column--2iymX h4 a")
    for card in cards:
        result.append(card.get_attribute('href'))

    return result

def book_table_contents(href):
    browser.get(href)
    result = set([])
    btc = browser
    title = btc.find_element_by_css_selector("h1.t-title").text
    isbn = btc.find_element_by_css_selector("div.t-isbn").text
    print("title = "+title+ "  isbn = "+isbn)
    table_contents = btc.find_elements_by_css_selector("ol.detail-toc li > a")
    for tc in table_contents:
        li = tc.get_attribute("href").split("#")[0]
        #print(tc.text)
        result.add(li)
    
    return result

def get_book_content_html(href):
    browser.get(href)
    return browser.find_element_by_css_selector("body").get_attribute('innerHTML')
    #return browser.find_element_by_css_selector("div.sbo-rt-content").get_attribute('innerHTML')

def db_save(data):
    cur = conn.cursor()
    for dd in data:
        cur.execute("insert into books(href, content) values(?, ?)", dd)
    conn.commit()



login(user, password)

book_link_list = get_book_link_listBysearch_page("", 0)

for link in book_link_list:
    table_link = book_table_contents(link)
    books_data = []
    for tl in table_link:
        books_data.append((tl, get_book_content_html(tl)))
    db_save(books_data)
        
