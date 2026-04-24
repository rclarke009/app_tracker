I will add the url and the screen contents and which resume i'm using.

i will paste them into a google form and click submit
app_entry_form


the app will grab that and get relevant info and append 
it to the app_tracker google sheet along with that day's date.



Either leave Root Directory empty and use start command:
gunicorn web_app.app:app
Or set Root Directory to web_app and use:
gunicorn app:app
(then the module is just app, not web_app.app).

gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000


