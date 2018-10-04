import json


def decode(request):
    if not request.is_json:
        return "wrong"
    content = request.get_json()
    print(content)
    return content["api"] + " data: " + content["data"]