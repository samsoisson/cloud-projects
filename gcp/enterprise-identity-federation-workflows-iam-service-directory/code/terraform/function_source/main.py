if __name__ == '__main__':
    # For local testing
    import flask
    app = flask.Flask(__name__)
    
    @app.route('/', methods=['POST'])
    def local_provision():
        return provision_identity(flask.request)
    
    @app.route('/health', methods=['GET'])
    def local_health():
        return health_check(flask.request)
    
    app.run(debug=True, host='127.0.0.1', port=8080)