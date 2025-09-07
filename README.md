# E-Commerce Store

A Django-based e-commerce application.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Abhijeet4002/ecommerce_project.git
   cd ecommerce_project
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up `.env`:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

5. Make migrations and run:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Deployment

To deploy on Heroku:

1. Add `Procfile`, `runtime.txt`, and commit.
2. Push to Heroku.
3. Set environment variables.
4. Run migrations and collect static files.

## License

MIT
