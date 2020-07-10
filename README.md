# image-resizer
Service to resize images asynchronously

Django-based app, using Celery+Redis to handle resize requests asynchronously

## Setting up

#### 1. Start Redis server as a message broker for Celery  
Run:
```bash
  $ redis-server
```
#### 2. Start Celery workers  
Inside image_resizer/image_resizer directory run:
```bash
  $ celery worker -A image_resizer --loglevel=info --concurrency=3
```
#### 3. Launch server  
Inside image_resizer directory run:
```bash
  $ python manage.py runserver
```

## Test

Inside image_resizer directory run:
```bash
  $ python manage.py test
```
## API Info

#### 1. Create task to resize image
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
  
  
#### 2. Check for task status and result image  
URL structure:
```
  http://host_name/api/<task_id>
```
Method: GET

Parameters: None

Returns:  
'task_status': 'PENDING', 'SUCCESS' or 'FAILURE' -- current status of task  
'task_id': id of requested task  
'img_path': returned if task_status == 'SUCCESS', url to download resulting image  

Example:  
```curl
  curl --location --request GET '127.0.0.1:8000/api/task/0e62c1b1-47eb-4aac-8168-9ec5a75f44f7'
```

Example response:
```
{
    "task_status": "SUCCESS",
    "task_id": "0e62c1b1-47eb-4aac-8168-9ec5a75f44f7",
    "img_path": "/media/images/gift_idea_2000x2000_100x100.png"
}
```
