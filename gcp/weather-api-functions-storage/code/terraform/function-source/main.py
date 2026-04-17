@app.route('/')
def test_endpoint():
    from flask import request
    return weather_api(request)

# Change host from '0.0.0.0' to '127.0.0.1' to avoid binding to all network interfaces
app.run(host='127.0.0.1', port=8080, debug=True)