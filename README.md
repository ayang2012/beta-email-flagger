# beta-email-flagger
## Technologies Used
- flask, google api, gunicorn, nginx, poetry
## How to run
- `poetry run gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app`
- `https://localhost`