"""
Thin wrapper used to start web service
"""

from application.oauth_app_api import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=app.config['DEBUG'])
