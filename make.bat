CALL venv\Scripts\activate
pyinstaller --noconfirm --clean --noconsole --add-binary "./interface.ui;./"  app.py