import azure.functions as func
import os
import json
import pyodbc

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ---- Fill in your Azure SQL connection details here ----
# (Better practice: set these as Application Settings / env vars
# instead of hardcoding, but keeping it simple for the assignment)
server = 'inclassassignment.database.windows.net'
database = 'in-class-assignment-db'
username = 'xavier-admin'
password = 'Password1'
# ----------------------------------------------------------


def get_db_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=" + server + ";"
        "DATABASE=" + database + ";"
        "UID=" + username + ";"
        "PWD=" + password + ";"
        "ENCRYPT=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )


@app.route(route="login", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def login(req: func.HttpRequest) -> func.HttpResponse:
    req_username = req.params.get("username")
    req_password = req.params.get("password")

    if not req_username or not req_password:
        return func.HttpResponse("Missing username or password", status_code=400)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (req_username, req_password)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return func.HttpResponse(
            json.dumps({
                "message": "Login Successful",
                "username": req_username
            }),
            mimetype="application/json",
            status_code=200
        )
    else:
        return func.HttpResponse("invalid", status_code=200)
