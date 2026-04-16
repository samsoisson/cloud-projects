if __name__ == '__main__':
    # For local testing
    import flask

    app = flask.Flask(__name__)

    @app.route('/', methods=['GET'])
    def test_function():
        request = flask.request
        return generate_compliance_report(request)

    app.run(debug=True, port=8080)
