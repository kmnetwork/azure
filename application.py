import mysql.connector
from mysql.connector import Error
from configparser import ConfigParser
import json, requests, sys
import pprint
from json2html import *
from flask import Flask,render_template, request, Response


app = Flask(__name__) 
 
def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
 
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
 
    return db 

def connectx():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='mkiss.mysql.database.azure.com',
		                               port=3306,
                                       database='python_mysql',
                                       user='mkissroot@mkiss',
                                       password='Almafa1.',
									   ssl_ca='ssl/trust.pem')
        if conn.is_connected():
            print('Connected to MySQL database')
 
    except Error as e:
        print(e)
 
    finally:
        conn.close()
 
 
def query_with_fetchone():
    try:
        dbconfig = read_db_config()
        conn = mysql.connector.MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
 
        row = cursor.fetchone()
 
        while row is not None:
            print(row)
            row = cursor.fetchone()
 
    except Error as e:
        print("*exception*")
        print(e)
 
    finally:
        cursor.close()
        conn.close()

def query_with_fetchall():
    rows=[]
    try:
        dbconfig = read_db_config()
        conn = mysql.connector.MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
         
        print('Total Row(s):', cursor.rowcount)
        for row in rows:
            print(row)
            print(type(row))			
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()
    return(rows) 
	
	
def query_to_json(query, args=(), one=False):
    rows=[]
    try:
        dbconfig = read_db_config()
        conn = mysql.connector.MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = [dict((cursor.description[i][0], value) \
            for i, value in enumerate(row)) for row in cursor.fetchall()]
         
        print('Total Row(s):', cursor.rowcount)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()
    
    if rows:
        if one: 
            retval = rows[0]
        else:
            retval = rows
    else:
        retval = None 	
	
    return(retval) 	
 
def iter_row(cursor, size=10):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row 
 

def query_with_fetchmany():
    try:
        dbconfig = read_db_config()
        conn = mysql.connector.MySQLConnection(**dbconfig)
        cursor = conn.cursor()
 
        cursor.execute("SELECT * FROM books")
 
        for row in iter_row(cursor, 10):
            print(row)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close() 


@app.route('/', methods=['GET'])
def index():
    return "Hello Nuclear Geeks"
	
@app.route('/books', methods=['GET', 'POST'])
def books():
    table_data = query_to_json("SELECT * FROM books",None,False)
    my_html = "<html>Table: books<BR>"
    my_html = my_html + json2html.convert(json = table_data)
    my_html = my_html + "<BR></html>"
    return(my_html)

@app.route('/writers', methods=['GET'])
def writers():
    table_data = query_to_json("SELECT * FROM authors",None,False)
    my_html = "<html>Table: authors<BR>"
    my_html = my_html + json2html.convert(json = table_data)
    my_html = my_html + "<BR></html>"
    return(my_html)	
	
@app.route('/writersjson', methods=['GET'])
def writersjson():
    table_data = query_to_json("SELECT * FROM authors",None,False)
    	
    return Response(json.dumps(table_data),mimetype='application/json')	
	
@app.route('/wheather',methods=['GET'])
def wheather():
    url = "http://api.openweathermap.org/data/2.5/weather?id=3046526&APPID=8f6abb37f67a3cb3dcef2f6023a92641&units=metric&mode=html"
    response = requests.get(url)
    response.raise_for_status()	
    current_wheather = response.text
    table_data = query_to_json("SELECT * FROM authors",None,False)
    my_html = current_wheather # + "<BR>"
    my_html = my_html + "<html>Table: authors<BR>"
    my_html = my_html + json2html.convert(json = table_data)
    my_html = my_html + "<BR></html>"
    return(my_html)	
	

	
	