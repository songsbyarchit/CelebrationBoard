from app import app
import os

if __name__ == '__main__':
    # Get the port from environment variable, default to 5000 if not set
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app, listening on all network interfaces (0.0.0.0) for external requests
    app.run(host='0.0.0.0', port=port, debug=True, ssl_context=None)