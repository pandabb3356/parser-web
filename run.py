from web import create_app

app = create_app()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Development Server Help')
    parser.add_argument("-d", "--debug", action="store_true", dest="debug",
                        help="run in debug mode (for use with PyCharm)", default=False)
    parser.add_argument("-p", "--port", action="store", dest="port", type=int,
                        help="listening port", default=5300)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=True)


