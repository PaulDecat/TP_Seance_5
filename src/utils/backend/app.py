from flask import Flask
from routes.actions import actions_bp
from routes.analytics import analytics_bp
from routes.auth import auth_bp
from routes.recommendations import rec_bp
from routes.upload import upload_bp

app = Flask(__name__)
app.register_blueprint(upload_bp)
app.register_blueprint(actions_bp)
app.register_blueprint(rec_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
	app.run(debug=True)