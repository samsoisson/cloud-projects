if __name__ == "__main__":
    from flask import Flask, request as flask_request
    
    app = Flask(__name__)
    
    @app.route('/', methods=['GET', 'POST', 'OPTIONS'])
    def local_weather_api():
        return weather_api(flask_request)
    
    @app.route('/health', methods=['GET'])
    def local_health_check():
        return health_check()
    
    print("Starting local development server...")
    print("Weather API available at: http://127.0.0.1:8080")
    print("Health check available at: http://127.0.0.1:8080/health")
    print("Example: http://127.0.0.1:8080?city=Tokyo")
    
    app.run(host='127.0.0.1', port=8080, debug=True)