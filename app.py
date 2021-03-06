from selenium import webdriver
import sqlite3

# 로그인, 책 목록 가져오기, 책정보 저장하기, 책 목차 가져오기, 책 내용 저장하기
# 목차에서 같은 링크일 경우..., 목차 트리구조
# 책 파싱 => md?
# =====DB=====
# book isbn, publisher, title, releaseDate
# menu idx, isbn, href, title, parent
# content idx, menu, content

user = "wkzkfmxk23@gmail.com"
password = ""
conn = sqlite3.connect("book.sqlite")

browser = webdriver.PhantomJS()
browser.implicitly_wait(2)

# 로그인
def login(user, password):
    url_login = "https://learning.oreilly.com/accounts/login/"
    browser.get(url_login)
    
    browser.find_element_by_id("id_email").send_keys(user)
    browser.find_element_by_id("id_password1").send_keys(password)
    
    form = browser.find_element_by_css_selector("input#login[type=submit]")
    form.submit()
# 책 리스트
def get_book_link_listBysearch_page(search, page):
    url_list = "https://learning.oreilly.com/search/?query={search}&extended_publisher_data=true&highlight=true&include_assessments=false&include_case_studies=true&include_courses=true&include_orioles=true&include_playlists=true&is_academic_institution_account=false&formats=book&sort=date_added&page={page}"
    browser.get(url_list.format(search=search, page=page))
    result = []
    cards = browser.find_elements_by_css_selector("article.column--2iymX h4 a")
    for card in cards:
        result.append(card.get_attribute('href'))

    return result
# 책 페이지 리턴
def get_book_page_html(href):
    return browser.get(href)
# 책 정보 리턴
def get_book_info(page):
    # div.review-report data-identifier:isbn data-title:title
    # div.t-authors 저자
    # div.t-publishers 출판사
    # div.t-release-date 출판일
    # div.title-description t-description sbo-reader-content 책 설명
    result = [page.find_element_by_css_selector("div.t-isbn").text, page.find_element_by_css_selector("h1.t-title").text]
    return result
# 책 메뉴 리턴 리뉴얼
def get_book_menu(page):
    result = []
    table_contents = page.find_elements_by_css_selector("ol.detail-toc li > a")
    for tc in table_contents:
        title = tc.text
        link = tc.get_attribute("href").split("#")[0]
        result.append((title, link))
    return result
# 책 메뉴 리턴
def book_table_contents(href):
    browser.get(href)
    result = set([])
    btc = browser
    table_contents = btc.find_elements_by_css_selector("ol.detail-toc li > a")
    for tc in table_contents:
        li = tc.get_attribute("href").split("#")[0]
        result.add(li)
    
    return result
# 책 내용 설정
def set_book_content(menu):
    for m in menu:
        m.content = get_book_content_html(m.link)
    return menu
# 책 내용 리턴
def get_book_content_html(href):
    browser.get(href)
    return browser.find_element_by_css_selector("body").get_attribute('innerHTML')
    #return browser.find_element_by_css_selector("div.sbo-rt-content").get_attribute('innerHTML')
# 책 DB 저장
def db_book_save(data):
    cur  = conn.cursor()
    cur.execute("insert into book(isbn, title) values(?, ?)", data)
    conn.commit()
# 책 내용 DB 저장
def db_content_save(data):
    cur = conn.cursor()
    for c in data:
        cur.execute("insert into book_content(href, content) values(?, ?)", c)
    conn.commit()
# 



login(user, password)

book_link_list = get_book_link_listBysearch_page("", 0)

# for link in book_link_list:
#     table_link = book_table_contents(link)
#     books_data = []
#     for tl in table_link:
#         books_data.append((tl, get_book_content_html(tl)))
#     db_content_save(books_data)
        
for link in book_link_list:
    book_html = get_book_page_html(link)
    book_info = get_book_info(book_html)
    book_menu = get_book_menu(book_html)

    db_book_save(book_info)
