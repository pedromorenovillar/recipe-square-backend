## Project structure

```bash
recipe-square-backend/
│
├── app/
│   ├── __init__.py          # Initializes the Flask app
│   ├── routes.py            # Defines API routes
│   ├── db.py                # MongoDB connection logic
│   ├── mail.py              # Initializes mail for password recovery
│   └── config.py            # Configuration settings
│
├── Pipfile                  # Dependencies for python
├── Pipfile-lock             # Dependencies for python
├── Procfile                 # Gunicorn config for Heroku
├── README.md                # Project structure
├── requirements.txt         # Dependencies
└── run.py                   # Main entry point to run the Flask app
```
