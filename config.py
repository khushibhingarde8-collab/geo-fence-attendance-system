from flask_mysqldb import MySQL

mysql = MySQL()

def init_mysql(app):

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Vaishu@18'
    app.config['MYSQL_DB'] = 'company_portal_2'

    mysql.init_app(app)