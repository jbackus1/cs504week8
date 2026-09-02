import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(rout="hello")
def hello(req):
  return func.HttpResponse("Hello")
