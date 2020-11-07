import flask
from flask_paginate import Pagination, get_page_parameter, get_per_page_parameter

def journalDashboardLogic(mysql):

    journal_list = []  # list initializing
    returnedQueries = []

    #global mysql
    cursor = mysql.connection.cursor()

    pagination = None

    try:
        page = flask.request.args.get(get_page_parameter(), type=int, default=1)
        print('--Page number-- ', page)
    except ValueError:
        page = 1

    # fetch the journal name parameter from searchResults page
    journal_name = str(flask.request.args.get("journalName"))
    sql = "Select doi, title, container_title, issue, page, published_print_date_parts, fk from _main_ where container_title like '%" + journal_name + "%\';"

    cursor.execute(sql)
    result_set = cursor.fetchall()

    # iterate the result set
    for row in result_set:
        # get fk from _main_ table
        fk = row['fk']
        author_list = []
        if fk is not None:
            # look up author table by fk
            author_sql = "select id,name from author where fk = " + \
                str(fk) + ";"
            cursor.execute(author_sql)
            # get list of authors for given fk
            author_list = cursor.fetchall()

        # create dict with _main_ table row and author list
        article = {'objectID': row['doi'], 'articleTitle': row['title'],
                   'journalName': row['container_title'],
                   'issue': row['issue'],
                   'journalPage': row['page'],
                   'articleDate': row['published_print_date_parts'],
                   'author_list': author_list}
        journal_list.append(article)

    start_year = 1995
    end_year = 2020
    publishedPerYear = []
    while (start_year <= end_year):
        articles_per_year_sql = "select count(*) count " \
                                "from dr_bowman_doi_data_tables._main_ " \
                                "where container_title like '%" + journal_name + "%' " \
                                "and substr(published_print_date_parts,1,4)='" + str(
                                    start_year) + "' ;"
        cursor.execute(articles_per_year_sql)
        yr_count = cursor.fetchone()
        publishedPerYear.append(yr_count["count"])
        start_year = start_year + 1

    per_page = 10  # article count per page
    article_start = (page * per_page) - 10  # calculate starting article index (for any given page)
    article_end = article_start + 10  # calculate ending article index (for any given page)

    journal_url_param = "/journalDashboard?journalName=" + journal_name + "&page={0}"

    # form a pagination object
    pagination = Pagination(page=page, per_page=per_page, href=journal_url_param,
                            total=len(journal_list), css_framework='bootstrap4')

    return flask.render_template('journalDashboard.html',
                                 journal_name=journal_name,
                                 journal_list=journal_list,
                                 publishedPerYear=publishedPerYear,
                                 pagination=pagination,
                                 article_start=article_start,
                                 article_end=article_end
                                 )
