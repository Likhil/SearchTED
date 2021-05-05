from flask import Flask, render_template, request, url_for, redirect
from elasticsearch import Elasticsearch, RequestsHttpConnection
import ssl
from elasticsearch.connection import create_ssl_context
import os
import warnings
warnings.filterwarnings("ignore")
import os
app = Flask(__name__)

DEBUG = os.environ.get("FLASK_DEBUG") == "1"
app.config.update(DEBUG=DEBUG, JSON_PRETTYPRINT_REGULAR=DEBUG)
@app.route("/")
def main():
    return render_template("home.html")


context = create_ssl_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
es = Elasticsearch(
    ['tux-es1.cci.drexel.edu','tux-es2.cci.drexel.edu','tux-es3.cci.drexel.edu'],
    http_auth=('lkr46', 'eiKaeCoi9eek'),
    scheme="https",
    port=9200,
    ssl_context = context,
)

@app.route('/search', methods=['POST','GET'])
def search():
    keywords = request.form['searchQuery']
    tags=request.form['tag']
    if tags != "":
        query_body = {
            "query": {
                "bool":{
                    "must":[
                        {
                            "multi_match" : {
                            "query": keywords,
                            "fields": ["description", "title", "main_speaker","speaker_occupation"]
                            }}
                        ],
                    "should": [
                        { "rank_feature": {"field": "views","boost":15.0 }
                        }],
                    "filter": [
                        { "term": {"tags": tags}}]
            }
        }}

    else:
        query_body = {
            "query": {
                "bool":{
                    "must":[
                        {
                            "multi_match" : {
                            "query": keywords,
                            "fields": ["description", "title", "main_speaker","speaker_occupation"]
                            }}
                        ],
                    "should": [
                        { "rank_feature": {"field": "views","boost":15.0 }
                        }]
            }
        }}

    res = es.search(index="lkr46_info624_201904_ted_search", body=query_body)
    return render_template("results.html",res=res)


if __name__ == "__main__":
    app.run()
