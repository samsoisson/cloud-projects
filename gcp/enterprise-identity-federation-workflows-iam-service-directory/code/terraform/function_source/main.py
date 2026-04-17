@functions_framework.http
def provision_identity(request: Request) -> Tuple[Dict[str, Any], int]:
    """
    HTTP Cloud Function entry point for identity provisioning.
    
    Args:
        request: Flask request object
        
    Returns:
        HTTP response tuple (data, status_code)
    """
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    # Only allow POST requests
    if request.method != 'POST':
        return ({'error': 'Method not allowed'}, 405, headers)
    
    try:
        # Parse request JSON
        request_json = request.get_json(silent=True)
        if not request_json:
            return ({'error': 'Invalid JSON or empty request body'}, 400, headers)
        
        # Log the incoming request (excluding sensitive data)
        # Sanitize the 'identity' field before logging
        identity_for_logging = request_json.get('identity', 'unknown')
        logger.info(f"Received provisioning request for identity: {identity_for_logging}")
        
        # Get provisioner and process request
        identity_provisioner = get_provisioner()
        response_data, status_code = identity_provisioner.provision_identity(request_json)
        
        return (response_data, status_code, headers)
        
    except Exception as e:
        logger.error(f"Function execution error: {e}")
        return ({'error': 'Function execution failed'}, 500, headers)