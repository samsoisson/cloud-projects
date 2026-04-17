__main__ = '__main__'
if __name__ == '__main__':
    # For local testing
    import flask
    
    app = flask.Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def test_function():
        request = flask.request
        return generate_compliance_report(request)
    
    # Bind only to localhost to avoid exposing to all network interfaces
    app.run(debug=True, host='127.0.0.1', port=8080)