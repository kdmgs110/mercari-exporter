from Flask import Flask, render_template, flash, redirect, url_for, session, request, logging, Response
import sys
import os
from selenium import webdriver
import pandas
import time


app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/", methods=["POST"])
def post():
    query = request.form["query"]
    csv = exportCSV(query)
    with open("output.csv") as fp:
            csv = fp.read()
            return Response(
                csv,
                mimetype="text/csv",
                headers={"Content-disposition":
                         "attachment; filename=output.csv"})


def exportCSV(query):
    #browser = webdriver.Chrome(executable_path='/mnt/c/workspace/pydev/chromedriver.exe') #ローカル
    browser = webdriver.PhantomJS()#heroku
    df = pandas.read_csv('default.csv', index_col=0)
    query = query
    browser.get("https://www.mercari.com/jp/search/?sort_order=price_desc&keyword={}&category_root=&brand_name=&brand_id=&size_group=&price_min=&price_max=".format(query))
    page = 1
    while True: #continue until getting the last page
        if len(browser.find_elements_by_css_selector("li.pager-next .pager-cell:nth-child(1) a")) > 0:
            print("######################page: {} ########################".format(page))
            print("Starting to get posts...")
            posts = browser.find_elements_by_css_selector(".items-box")
            for post in posts:
                title = post.find_element_by_css_selector("h3.items-box-name").text
                price = post.find_element_by_css_selector(".items-box-price").text
                price = price.replace('¥', '')
                sold = 0
                if len(post.find_elements_by_css_selector(".item-sold-out-badge")) > 0:
    	            sold = 1
                url = post.find_element_by_css_selector("a").get_attribute("href")
                se = pandas.Series([title, price, sold,url],['title','price','sold','url'])
                df = df.append(se, ignore_index=True)
            page+=1
            btn = browser.find_element_by_css_selector("li.pager-next .pager-cell:nth-child(1) a").get_attribute("href")
            print("next url:{}".format(btn))
            browser.get(btn)
            print("Moving to next page......")
        else:
            print("no pager exist anymore")
            break
    df.to_csv("output.csv")

if __name__ == '__main__':
    #app.run(debug=True) # デバックしたときに、再ロードしなくても大丈夫になる
    app = Flask()
