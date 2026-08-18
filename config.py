from flask_mysqldb import MySQL

mysql = MySQL()

def init_mysql(app):

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'username'
    app.config['MYSQL_PASSWORD'] = 'your_password'
    app.config['MYSQL_DB'] = 'company_portal'

    mysql.init_app(app)