if __name__ == '__main__':
    # Run the Flask application
    port = int(os.environ.get('PORT', 8080))
    app.run(host='127.0.0.1', port=port, debug=False)