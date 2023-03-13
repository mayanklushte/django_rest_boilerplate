### Dependencies
```
python v3.9
pip v20.3.3
```

### Local python setup (optional)
```
cd <project root>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Copy environment file
```
cp .env.development .env;
```


### Migrate database
```
python manage.py makemigrations;
python manage.py migrate;
```

### Run Server Locally
```
python manage.py runserver
```
