from app import app    #imprt the app we made

if __name__ == '__main__':
    app.run(debug=True, ssl_context=None)    #disable ssl for development