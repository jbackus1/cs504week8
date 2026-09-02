import azure.functions as func
import os
import json
import logging
import pymssql

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ---- Azure SQL connection details ----
# Pulled from Application Settings (env vars) so nothing sensitive is
# committed to source control. Set these in the Function App's
# Configuration blade (or in local.settings.json for local runs):
#   SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD
server = os.environ.get("SQL_SERVER", "inclassassignment.database.windows.net")
database = os.environ.get("SQL_DATABASE", "in-class-assignment-db")
username = os.environ.get("SQL_USERNAME", "xavier-admin")
password = os.environ.get("SQL_PASSWORD", "Password1")
# ----------------------------------------------------------


def get_db_connection():
    return pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        login_timeout=30
    )


@app.route(route="login", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def login(req: func.HttpRequest) -> func.HttpResponse:
    req_username = req.params.get("username")
    req_password = req.params.get("password")

    if not req_username or not req_password:
        return func.HttpResponse("Missing username or password", status_code=400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (req_username, req_password)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        # Full details go to Log Stream / Application Insights so the
        # real cause is visible there instead of a bare 500.
        logging.exception("Login route failed while querying the database")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

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
