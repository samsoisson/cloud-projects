        # Log the incoming request (excluding sensitive data)
        logger.info("Received provisioning request")
    app.run(host='127.0.0.1')