from api import API
from webob import Request, Response


app = API()

@app.route("/test")
def test():
    print("HERE")
    
print(test())

@app.route("/home")
def home(request: Request, response):
    response.text = "[home] hello"


@app.route("/about")
def about(request, response, name):
    # `name` is a query parameter
    response.text = f"[about] hello {name}"


@app.route("/movie/{name}")
def movie(request, response, name):
    response.text = f"[movie] hello {name}"


@app.route("/book")
class BooksResource:
    def get(self, req, response):
        response.text = "[book] GET"

    def post(self, req, response):
        response.text = "[book] POST"

