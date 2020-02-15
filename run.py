from jamaica import app

if __name__ == '__main__':
    # https://stackoverflow.com/questions/7023052/configure-flask-dev-server-to-be-visible-across-the-network/51164848
    app.run(host='0.0.0.0')
