from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    Config.init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)