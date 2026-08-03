# from flask import Flask
# from flask_mail import Mail
# from app import app

# if __name__ == "__main__":
#     app.run(debug=True)

# app = Flask(__name__)

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'info@pceengineering.com'
# app.config['MAIL_PASSWORD'] = 'cyco lmhe hwem paxg'

# mail = Mail(app)

# import routes
# import mail_service

# print(app.url_map)


# if __name__ == "__main__": 
#     app.run(debug=True)


from app import app
import routes
import mail_service

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )