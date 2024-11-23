from app import app
import os

if __name__ == '__main__':
    # Use the PORT environment variable for Render, otherwise default to 5001 for local dev
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True, ssl_context=None)