from flask_cors import CORS
import os
from app import app
import util.util as util
import services.org as org
import services.user as user
import services.two_factor as two_fa


CORS(app, resources={r"/*": {"origins": "*"}})
app.config['MAIL_SERVER'] = os.getenv('SMTP_SERVER')
app.config['MAIL_PORT'] = os.getenv('SMTP_PORT')
app.config['MAIL_USERNAME'] = os.getenv('EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

if __name__ == '__main__':
    state = util.init()
    if state is not None:
        # user.setInit(state[0],state[1],state[2])
        # two_fa.setInit(state[0],state[1],state[2])
        app.register_blueprint(org.org_bp,url_prefix='/org')
        app.register_blueprint(user.user_bp,url_prefix='/user')
        app.register_blueprint(two_fa.two_fa_bp,url_prefix='/user/two_factor')
        app.run(host='0.0.0.0', port=8080, debug=True)
