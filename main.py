from backend import app, db

with app.app_context():
    db.create_all()
    print('Database created!')

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)