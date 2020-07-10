# image-resizer
Service to resize images asynchronously

Django-based app, using Celery+Redis to handle resize requests asynchronously

## Setup

1. Run:
```bash
  $ redis-server
```
2. Inside image_resizer/image_resizer directory run:
```bash
  $ celery worker -A image_resizer --loglevel=info --concurrency=3
```
3. Inside image_resizer directory run:
```bash
  $ python manage.py runserver
```

## Test

Inside image_resizer directory run:
```bash
  $ python manage.py test
```
