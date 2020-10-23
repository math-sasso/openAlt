# pip install flask-mysqldb
import flask
import json
from flask_mysqldb import MySQL
app = flask.Flask(__name__)

# Database connection settings
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
# Or use the database.table which will allow us to join the databases - the one with author, and the one with events
app.config['MYSQL_DB'] = 'dr_bowman_doi_data_tables'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Database initialization and cursor
mysql = MySQL(app)


########## connect to cross ref database
app2 = flask.Flask(__name__)

# Database connection settings
app2.config['MYSQL_USER'] = 'root'
app2.config['MYSQL_PASSWORD'] = ''
# Or use the database.table which will allow us to join the databases - the one with author, and the one with events
app2.config['MYSQL_DB'] = 'crossrefeventdata'
app2.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Database initialization and cursor
mysql2 = MySQL(app2)


@app.route('/')
def index():

    return flask.render_template('index.html')


@app.route('/searchResultsPage', methods=["GET", "POST"])
def homepageSearch():

    # Initialize variables - need to use global mysql variable
    global mysql
    cursor = mysql.connection.cursor()

    returnedQueries = []

    x = "something not none"
    row = "something not none"
    # Get the parameters from
    if flask.request.method == "POST":
        search = str(flask.request.form.get("search"))
        selection = str(flask.request.form.get("dropdownSearchBy"))
        selcted_years = flask.request.form.getlist("years")

        for year in range(0, len(selcted_years)):
            selcted_years[year] = int(selcted_years[year])

        if not selcted_years:
            years = [{'year': 2020, 'select': ''},
                     {'year': 2019, 'select': ''},
                     {'year': 2018, 'select': ''},
                     {'year': 2017, 'select': ''},
                     {'year': 2016, 'select': ''},
                     {'year': 1997, 'select': ''}]  # TBD bring unique years from main table
        else:
            years = [{'year': 2020, 'select': ''},
                     {'year': 2019, 'select': ''},
                     {'year': 2018, 'select': ''},
                     {'year': 2017, 'select': ''},
                     {'year': 2016, 'select': ''},
                     {'year': 1997, 'select': ''}]

            for year in years:
                if year.get('year') in selcted_years:
                    year['select'] = 'checked'
    # form query string for year filter constraint in where clause
    s_years = '( '
    for year in selcted_years:
        if year == selcted_years[-1]:
            s_years = s_years + "'" + str(year) + "'"
        else:
            s_years = s_years + "'" + str(year) + "'" + ","
    s_years = s_years + ')'

    # Search by DOI - WORKING
    if (selection == "DOI"):

        if not selcted_years:
            # no year filter
            sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where doi like '%" + search + "%\';"
        else:
            # with year filter
            sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where doi like '%" + \
                search + \
                "%\' and substr(published_print_date_parts, 1,4) in " + \
                s_years+";"

        cursor.execute(sql)
        result_set = cursor.fetchall()

        # iterate the _main_ table result set
        for row in result_set:
            # get fk from _main_ table
            fk = row['fk']
            author_list = []
            if fk is not None:
                # look up author table by fk
                author_sql = "select id, name from author where fk = " + \
                    str(fk) + ";"
                cursor.execute(author_sql)
                # get list of authors for given fk
                author_list = cursor.fetchall()

            # create dict with _main_ table row and author list
            article = {'objectID': row['doi'], 'articleTitle': row['title'],
                       'journalName': row['publisher'],
                       'articleDate': row['published_print_date_parts'],
                       'author_list': author_list}
            # append article dict to returnedQueries list
            returnedQueries.append(article)

        returnedQueries.append(None)
        cursor.close()
        returnedQueries.pop()  # the last list item is always null so pop it

    # THIS DOES NOT WORK YET SINCE AUTHOR TABLE NOT FILLED IN
    elif (selection == "Author"):
        # get fk and name for searched author name
        given_author = []
        given_author = '( '
        auth_sql = "SELECT fk, name FROM dr_bowman_doi_data_tables.author where name like'%" + search+"%';"
        cursor.execute(auth_sql)
        result_set = cursor.fetchall()
        # form a list of fk for the where statement (ex.) ('2005','2006')
        for row in result_set:
            if row == result_set[-1]:
                given_author = given_author + str(row['fk'])
            else:
                given_author = given_author + str(row['fk']) + ","
        given_author = given_author + ')'

        print(given_author)

        # query _main_ table with list of fk gotten previously
        if result_set is not None:
            if not selcted_years:
                # no year filter
                sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where fk in " + given_author + ";"
            else:
                # with year filter
                sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where fk in " + \
                    given_author + \
                    " and substr(published_print_date_parts, 1,4) in" + \
                    s_years + ";"

            print(sql)
            cursor.execute(sql)
            result_set = cursor.fetchall()

            # iterate the result set
            for row in result_set:
                # get fk from _main_ table
                fk = row['fk']
                author_list = []
                if fk is not None:
                    # look up author table by fk
                    author_sql = "select id, name from author where fk = " + \
                        str(fk) + ";"
                    cursor.execute(author_sql)
                    # get list of authors for given fk
                    author_list = cursor.fetchall()

                # create dict with _main_ table row and author list
                article = {'objectID': row['doi'], 'articleTitle': row['title'],
                           'journalName': row['publisher'],
                           'articleDate': row['published_print_date_parts'],
                           'author_list': author_list}
                # append article dict to returnedQueries list
                returnedQueries.append(article)

            returnedQueries.append(None)
            cursor.close()
            returnedQueries.pop()  # the last list item is always null so pop it

    # THIS DOES NOT WORK YET SINCE JOURNAL TABLE NOT FILLED IN
    elif (selection == "Journal"):
        if not selcted_years:
            # no year filter
            sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where publisher like '%" + search + "%\';"
        else:
            # with year filter
            sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where publisher like '%" + \
                search + \
                "%\' and substr(published_print_date_parts, 1,4) in" + \
                s_years+";"

        cursor.execute(sql)
        result_set = cursor.fetchall()

        # iterate the result set
        for row in result_set:
            # get fk from _main_ table
            fk = row['fk']
            author_list = []
            if fk is not None:
                # look up author table by fk
                author_sql = "select id, name from author where fk = " + \
                    str(fk) + ";"
                cursor.execute(author_sql)
                # get list of authors for given fk
                author_list = cursor.fetchall()

            # create dict with _main_ table row and author list
            article = {'objectID': row['doi'], 'articleTitle': row['title'],
                       'journalName': row['publisher'],
                       'articleDate': row['published_print_date_parts'],
                       'author_list': author_list}
            returnedQueries.append(article)

        returnedQueries.append(None)
        cursor.close()
        returnedQueries.pop()  # the last list item is always null so pop it

    # THIS DOES NOT WORK YET SINCE ARTICLE TABLE NOT FILLED IN
    elif (selection == "Article"):
        if not selcted_years:
            # no year filter
            sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where title like '%" + search + "%\';"
        else:
            # with year filter
            sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where title like '%" + \
                search + \
                "%\' and substr(published_print_date_parts, 1,4) in" + \
                s_years + ";"

        print(sql)
        cursor.execute(sql)
        result_set = cursor.fetchall()

        # iterate the result set
        for row in result_set:
            # get fk from _main_ table
            fk = row['fk']
            author_list = []
            if fk is not None:
                # look up author table by fk
                author_sql = "select id, name from author where fk = " + \
                    str(fk) + ";"
                cursor.execute(author_sql)
                # get list of authors for given fk
                author_list = cursor.fetchall()

            # create dict with _main_ table row and author list
            article = {'objectID': row['doi'], 'articleTitle': row['title'],
                       'journalName': row['publisher'],
                       'articleDate': row['published_print_date_parts'],
                       'author_list': author_list}
            returnedQueries.append(article)

        returnedQueries.append(None)
        cursor.close()
        returnedQueries.pop()  # the last list item is always null so pop it

    return flask.render_template('searchResultsPage.html',
                                 listedSearchResults=returnedQueries,
                                 years=years,
                                 dropdownSearchBy=selection,
                                 search=search)

# Article Dashboard


@app.route('/articleDashboard', methods=["GET", "POST"])
def articleDashboard():

    global mysql
    cursor = mysql.connection.cursor()

    global mysql2
    # connect to crossrefeventdata
    cursor2 = mysql2.connection.cursor()

    # get DOI parameter
    search = str(flask.request.args.get("DOI"))

    # query main table by DOI
    sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where doi like '%" + search + "%\';"

    cursor.execute(sql)
    mysql.connection.commit()
    article_result = cursor.fetchone()

    if article_result is not None:
        # get article fk
        fk = article_result['fk']

        # get list of authors for that fk
        if fk is not None:
            author_sql = "select name from author where fk = " + str(fk) + ";"
            cursor.execute(author_sql)
            author_list = cursor.fetchall()

        article = {'objectID': article_result['doi'], 'articleTitle': article_result['title'],
                   'journalName': article_result['publisher'],
                   'articleDate': article_result['published_print_date_parts'],
                   'author_list': author_list}

    cursor.close()

    # Size of each list depends on how many years(in chartScript.js) you'd like to display.
    # Queries will be inserted within the array
    years_list = [2016, 2017 ,2018, 2019, 2020]

    #cambia event
    cambiaEvent=[]
    for year in years_list:
        cambia_sql = "select count(*) count from crossrefeventdata.cambiaevent " \
                     "where substr(objectID,17)='"+article_result['doi']+"' " \
                     "and substr(occurredAt,1,4)='"+str(year)+"';"

        cursor2.execute(cambia_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        cambiaEvent.append(event_count['count'])
    print('cambiaEvent ~~~~~~~~~', cambiaEvent)
    #cambiaEvent = [30, 20, 50, 10, 90]  # TBD - delete this line after we upload data in cambia event table for all these years

    # crossrefevent
    crossrefevent = []
    for year in years_list:
        crossref_sql = "select count(*) count from crossrefeventdata.crossrefevent " \
                     "where substr(objectID,17)='" + article_result['doi'] + "' " \
                    "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(crossref_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        crossrefevent.append(event_count['count'])
    print(' crossrefevent ~~~~~~~~~~~', crossrefevent)
    #crossrefevent = [5, 7, 14, 18, 25]; # TBD - delete this line after we upload data in cambia event table for all these years

    # dataciteevent
    dataciteevent = []
    for year in years_list:
        datacite_sql = "select count(*) count from crossrefeventdata.dataciteevent " \
                       "where substr(objectID,17)='" + article_result['doi'] + "' " \
                        "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(datacite_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        dataciteevent.append(event_count['count'])
    print(' dataciteevent ~~~~~~~~~~~', dataciteevent)
    #dataciteevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # hypothesisevent
    hypothesisevent = []
    for year in years_list:
        hypothesis_sql = "select count(*) count from crossrefeventdata.hypothesisevent " \
                         "where substr(objectID,17)='" + article_result['doi'] + "' " \
                         "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(hypothesis_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        hypothesisevent.append(event_count['count'])
    print(' hypothesisevent ~~~~~~~~~~~', hypothesisevent)
    #hypothesisevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # newsfeedevent
    newsfeedevent = []
    for year in years_list:
        newsfeed_sql = "select count(*) count from crossrefeventdata.newsfeedevent " \
                         "where substr(objectID,17)='" + article_result['doi'] + "' " \
                         "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(newsfeed_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        newsfeedevent.append(event_count['count'])
    print(' newsfeedevent ~~~~~~~~~~~', newsfeedevent)
    # newsfeedevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # redditevent
    redditevent = []
    for year in years_list:
        reddit_sql = "select count(*) count from crossrefeventdata.redditevent " \
                       "where substr(objectID,17)='" + article_result['doi'] + "' " \
                       "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(reddit_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        redditevent.append(event_count['count'])
    print(' redditevent ~~~~~~~~~~~', redditevent)
    # redditevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # redditlinksevent
    redditlinksevent = []
    for year in years_list:
        redditlinks_sql = "select count(*) count from crossrefeventdata.redditlinksevent " \
                          "where substr(objectID,17)='" + article_result['doi'] + "' " \
                          "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(redditlinks_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        redditlinksevent.append(event_count['count'])
    print(' redditlinksevent ~~~~~~~~~~~', redditlinksevent)
    # redditlinksevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # stackexchangeevent
    stackexchangeevent = []
    for year in years_list:
        stackexchange_sql = "select count(*) count from crossrefeventdata.stackexchangeevent " \
                            "where substr(objectID,17)='" + article_result['doi'] + "' " \
                            "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(stackexchange_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        stackexchangeevent.append(event_count['count'])
    print(' stackexchangeevent ~~~~~~~~~~~', stackexchangeevent)
    # stackexchangeevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # twitterevent
    twitterevent = []
    for year in years_list:
        twitter_sql = "select count(*) count from crossrefeventdata.twitterevent " \
                            "where substr(objectID,17)='" + article_result['doi'] + "' " \
                            "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(twitter_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        twitterevent.append(event_count['count'])
    print(' twitterevent ~~~~~~~~~~~', twitterevent)
    # twitterevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # webevent
    webevent = []
    for year in years_list:
        web_sql = "select count(*) count from crossrefeventdata.webevent " \
                      "where substr(objectID,17)='" + article_result['doi'] + "' " \
                      "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(web_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        webevent.append(event_count['count'])
    print(' webevent ~~~~~~~~~~~', webevent)
    # webevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # wikipediaevent
    wikipediaevent = []
    for year in years_list:
        wikipedia_sql = "select count(*) count from crossrefeventdata.wikipediaevent " \
                  "where substr(objectID,17)='" + article_result['doi'] + "' " \
                  "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(wikipedia_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        wikipediaevent.append(event_count['count'])
    print(' wikipediaevent ~~~~~~~~~~~', wikipediaevent)
    # wikipediaevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years

    # wordpressevent
    wordpressevent = []
    for year in years_list:
        wordpress_sql = "select count(*) count from crossrefeventdata.wordpressevent " \
                        "where substr(objectID,17)='" + article_result['doi'] + "' " \
                        "and substr(occurredAt,1,4)='" + str(year) + "';"

        cursor2.execute(wordpress_sql)
        mysql2.connection.commit()
        event_count = cursor2.fetchone()
        wordpressevent.append(event_count['count'])
    print(' wordpressevent ~~~~~~~~~~~', wordpressevent)
    # wordpressevent = [5, 10, 15, 20, 25];  # TBD - delete this line after we upload data in cambia event table for all these years


    return flask.render_template('articleDashboard.html', article_detail=article,
                                 cambiaEventData=cambiaEvent,
                                 crossrefEventData=crossrefevent,
                                 dataciteEventData=dataciteevent,
                                 hypothesisEventData=hypothesisevent,
                                 newsfeedEventData=newsfeedevent,
                                 redditEventData=redditevent,
                                 redditlinksEventData=redditlinksevent,
                                 stackexchangeEventData=stackexchangeevent,
                                 twitterEventData=twitterevent,
                                 webEventData=webevent,
                                 wikipediaEventData=wikipediaevent,
                                 wordpressEventData=wordpressevent)

# Journal Dashboard


@app.route('/journalDashboard', methods=["GET", "POST"])
def journalDashboard():
    journal_list = []  # list initializing
    x = "something not none"
    global mysql
    cursor = mysql.connection.cursor()

    # fetch the journal name parameter from searchREsults page
    journal_name = str(flask.request.args.get("journalName"))
    sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where publisher like '%" + journal_name + "%\';"

    cursor.execute(sql)
    result_set = cursor.fetchall()

    # iterate the result set
    for row in result_set:
        # get fk from _main_ table
        fk = row['fk']
        author_list = []
        if fk is not None:
            # look up author table by fk
            author_sql = "select name from author where fk = " + str(fk) + ";"
            cursor.execute(author_sql)
            # get list of authors for given fk
            author_list = cursor.fetchall()

        # create dict with _main_ table row and author list
        article = {'objectID': row['doi'], 'articleTitle': row['title'],
                   'journalName': row['publisher'],
                   'articleDate': row['published_print_date_parts'],
                   'author_list': author_list}
        journal_list.append(article)

    # Size of each list depends on how many years(in chartScript.js) you'd like to display.
    # Queries will be inserted within the array
    cambiaEvent = [30, 20, 50, 10, 90]
    '''
    crossrefevent = [];
    dataciteevent = [];
    hypothesisevent = [];
    newsfeedevent = [];
    redditevent = [];
    redditlinksevent = [];
    stackexchangeevent = [];
    twitterevent = [];
    webevent = [];
    wikipediaevent = [];
    wordpressevent = [];
    '''

    return flask.render_template('journalDashboard.html',
                                 journal_name=journal_name,
                                 journal_list=journal_list, cambiaEventData=cambiaEvent)

# Author Dashboard


@app.route('/authorDashboard', methods=["GET", "POST"])
def authorDashboard():
    author_article_list = []

    global mysql
    cursor = mysql.connection.cursor()
    # fetch the query parameter author_id from searchResults page
    author_id = str(flask.request.args.get("author_id"))
    print('author_id', author_id)
    author_sql = "SELECT name, fk FROM dr_bowman_doi_data_tables.author where id ="+author_id+";"
    cursor.execute(author_sql)
    author_resultset = cursor.fetchone()

    author_name = author_resultset['name']
    author_fk = author_resultset['fk']
    if author_fk is not None:
        # look up author table by fk
        sql = "Select doi, title, publisher, published_print_date_parts, fk from _main_ where fk = " + \
            str(author_fk) + ";"
        cursor.execute(sql)
        result_set = cursor.fetchall()

        # iterate the result set
        for row in result_set:
            # get fk from _main_ table
            fk = row['fk']
            author_list = []
            if fk is not None:
                # look up author table by fk
                author_sql = "select id, name from author where fk = " + \
                    str(fk) + ";"
                cursor.execute(author_sql)
                # get list of authors for given fk
                author_list = cursor.fetchall()

            # create dict with _main_ table row and author list
            article = {'objectID': row['doi'], 'articleTitle': row['title'],
                       'journalName': row['publisher'],
                       'articleDate': row['published_print_date_parts'],
                       'author_list': author_list}
            author_article_list.append(article)
        cursor.close()

    # Size of each list depends on how many years(in chartScript.js) you'd like to display.
    # Queries will be inserted within the array
    cambiaEvent = [30, 20, 50, 10, 90]
    '''
    crossrefevent = [];
    dataciteevent = [];
    hypothesisevent = [];
    newsfeedevent = [];
    redditevent = [];
    redditlinksevent = [];
    stackexchangeevent = [];
    twitterevent = [];
    webevent = [];
    wikipediaevent = [];
    wordpressevent = [];
    '''

    return flask.render_template('authorDashboard.html',
                                 author_name=author_name,
                                 author_article_list=author_article_list, cambiaEventData=cambiaEvent)


@app.route('/about', methods=["GET", "POST"])
def about():

    return flask.render_template('about.html')


@app.route('/team', methods=["GET", "POST"])
def team():

    return flask.render_template('team.html')


@app.route('/licenses', methods=["GET", "POST"])
def licenses():

    return flask.render_template('licenses.html')


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
