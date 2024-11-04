## Backend repository for the Recipe Square Project

For detailed information about the project, please check the [frontend repository](https://github.com/pedromorenovillar/recipe-square-frontend).

## Backend languages

- Python with Flask
- MongoDB Cloud Atlas (for the DB) and Cloudinary (for recipe image storage)

## Backend structure

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

## Future improvements

- Add commenting feature API routes
- Add rating feature API routes