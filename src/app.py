from api import API


app = API()


@app.route("/home")
def home(request, response):
    response.text = "[home] hello"


@app.route("/about")
def about(request, response):
    response.text = "[about] hello"


@app.route("/movie/{name}")
def movie(request, response, name):
    response.text = "[movie] hello {name}"


@app.route("/book")
class BooksResource:
    def get(self, req, response):
        response.text = "[book] GET"

    def post(self, req, response):
        response.text = "[book] POST"
