import flask
from flask_mysqldb import MySQL
from flask import request, jsonify
from datetime import datetime
import os
# Import our functions for other pages
from web.searchLogic import searchLogic
from web.articleDashboardLogic import articleDashboardLogic
from web.journalDashboardLogic import journalDashboardLogic
from web.authorDashboardLogic import authorDashboardLogic
from web.landingPageStats import landingPageStats
from web.landingPageArticles import landingPageArticles
from web.landingPageJournals import landingPageJournals

from web.getPassword import getPassword

# get the users password from crossrefeventdata/web/passwd.txt
mysql_username = 'root'
#follow these commands
mysql_password = getPassword() #os.getenv(['MYSQL_PASSWORD'])#getPassword()
# https://stackoverflow.com/questions/39281594/error-1698-28000-access-denied-for-user-rootlocalhost
# Instantiate an object of class Flask
app = flask.Flask(__name__)
# Database connection settings
app.config['MYSQL_USER'] = mysql_username
app.config['MYSQL_PASSWORD'] = mysql_password
# Or use the database.table which will allow us to join the databases - the one with author, and the one with events
app.config['MYSQL_DB'] = 'dr_bowman_doi_data_tables'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Database initialization and cursor
mysql = MySQL(app)

# Instantiate a second object of class Flask
app2 = flask.Flask(__name__)
# Database connection settings
app2.config['MYSQL_USER'] = mysql_username
app2.config['MYSQL_PASSWORD'] = mysql_password

# Or use the database.table which will allow us to join the databases - the one with author, and the one with events
app2.config['MYSQL_DB'] = 'crossrefeventdatamain'
app2.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Database initialization and cursor
mysql2 = MySQL(app2)


@app.route('/')
def index():
    # Go to landingPageStats.py
    totalSum = landingPageStats(mysql)

    # Go to landingPageArticles.py
    totalSumArticles = landingPageArticles(mysql)

    # Go to landingPageJournals.py
    totalSumJournals = landingPageJournals(mysql)

    return flask.render_template('index.html', totalSum=totalSum, totalSumArticles=totalSumArticles, totalSumJournals=totalSumJournals)


@app.route('/searchResultsPage', methods=["GET", "POST"])
def search():

    # If a HTTPS POST Request is received...
    if(request.method == "POST"):
        dropdownValue = request.form.get('dropdownSearchBy')
    else:
        dropdownValue = str(flask.request.args.get("dropdownSearchBy"))

    # Go to searchLogic.py
    return searchLogic(mysql, mysql2, dropdownValue)


@app.route('/articleDashboard', methods=["GET", "POST"])
def articleDashboard():

    # Initialize years_list and yearInput.
    years_list = []
    yearInput = ''

    # Based on the current year, initialize the years_list list year range(5 years).
    # This is the default year range.
    currentYear = datetime.now().year
    for i in range(currentYear - 4, currentYear + 1):
        years_list.append(i)

    # If a HTTPS POST Request is received...
    if request.method == "POST":
        # Grab the year value from the year filter of the bar chart.
        if request.form.get('year') is not None:
            yearInput = request.form.get('year')
            yearInput = int(yearInput)
            years_list = []
            for i in range(yearInput - 2, yearInput + 3):
                years_list.append(i)

    # Go to articleDashboardLogic.py
    return articleDashboardLogic(mysql, mysql2, years_list, yearInput)


@ app.route('/journalDashboard', methods=["GET", "POST"])
def journalDashboard():

    # Get the current year so we can pass it to the graph X axis
    # The earliest year we consider is 1997
    years_list = []
    currentYear = datetime.now().year
    for i in range(1997, currentYear + 1):
        years_list.append(i)

    # Go to journalDashboardLogic.py
    return journalDashboardLogic(mysql, years_list)


@ app.route('/authorDashboard', methods=["GET", "POST"])
def authorDashboard():

    # Initialize years_list and yearInput.
    years_list = []
    yearInput = ''

    # Based on the current year, initialize the years_list list year range(5 years).
    # This is the default year range.
    currentYear = datetime.now().year
    for i in range(currentYear - 4, currentYear + 1):
        years_list.append(i)

    # If a HTTPS POST Request is received...
    if request.method == "POST":
        # Grab the year value from the year filter of the bar chart.
        if request.form.get('year') is not None:
            yearInput = request.form.get('year')
            yearInput = int(yearInput)
            years_list = []
            for i in range(yearInput - 2, yearInput + 3):
                years_list.append(i)

    # Go to authorDashboardLogic.py
    return authorDashboardLogic(mysql, mysql2, years_list, yearInput)


@ app.route('/about', methods=["GET", "POST"])
def about():
    return flask.render_template('about.html')


@ app.route('/team', methods=["GET", "POST"])
def team():
    return flask.render_template('team.html')


@ app.route('/licenses', methods=["GET", "POST"])
def licenses():
    return flask.render_template('licenses.html')


# If this is the main module or main program being run (app.py)......
if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
