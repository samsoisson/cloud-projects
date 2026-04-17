if __name__ == '__main__':
    # For local testing
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def test_endpoint():
        from flask import request
        return weather_api(request)
    
    app.run(host='127.0.0.1', port=8080, debug=True)