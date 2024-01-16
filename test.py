import requests
import unittest

url = "http://localhost"
port = 8000
host = f"{url}:{port}"


class BasicTest(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_extract_query_args(self):
        response = requests.get("{host}/movie/{name}".format(host=host, name="bo"))
        headers = response.headers.get("CONTENT-TYPE", None)

        if headers and "application/json" in headers:
            print(response.json())
        else:
            print(response.text)

        self.assertEqual(response.status_code, 200)

    def test_shadowed_paths(self):
        from src.api import API

        api = API()

        @api.route("/health")
        def fn1(requests, response):
            return api.default_response(response)

        with self.assertRaises(AssertionError):

            @api.route("/health")
            def fn2(requests, response):
                return api.default_response(response)

    def test_class_handler(self):
        url = f"{host}/book"
        verbs = ["post", "get"]
        for verb in verbs:
            attr = getattr(requests, verb, None)
            response = attr(url)
            self.assertEqual(response.status_code, 200)

        response = requests.put(url)
        self.assertEqual(response.status_code, 404)

    def test_get_query_params(self):
        url = f"{host}/about"
        name = "bo"
        response = requests.get(url, params=[("name", name)])
        self.assertEqual(response.text, f"[about] hello {name}")


if __name__ == "__main__":
    unittest.main()
