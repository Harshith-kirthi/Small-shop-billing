from app import app, db

# Ensure database tables are created inside the application context
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
