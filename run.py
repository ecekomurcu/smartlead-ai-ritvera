from app import create_app


app = create_app()


if __name__ == "__main__":
    #Debug değeri config.py içindeki çalışma ortamına göre belirlenir.
    app.run()
