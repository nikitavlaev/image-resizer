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
## API Info

1. Create task to resize image
URL structure:
```
  http://host_name/api/
```
Method: POST

Content-Type: multipart/form-data  

Parameters:  
'image_file': input image file, type: file  
'width': required width, type: int  
'height': required height, type: int  

Returns:  
'task_status': 'PENDING', 'SUCCESS' or 'FAILURE' -- current status of created task  
'task_id': id of task, so you can request its results

Example:  
```curl
  curl --location --request POST '127.0.0.1:8000/api/' \
  --form 'image_file=@/home/nikita/Downloads/gift_idea_2000x2000.png' \
  --form 'width=100' \
  --form 'height=100'  
```  
Example response:  
```
  {"task_status": "PENDING", "task_id": "8ee7e6fc-322a-4378-9a6e-26c0223534ad"}
```
