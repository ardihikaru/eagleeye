from ext_lib.utils import get_json_template, get_unprocessable_request_json


class StreamReader:
    def __init__(self):
        pass

    def read(self, request_json):
        print(request_json)
        return get_json_template(response=True, results=request_json, total=-1, message="OK")

