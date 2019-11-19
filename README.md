# news-restapi
### Overview
A simple JSON REST API for a News channel. Pure python, no dependencies.

Requires Python 3.7 or higher and sqlite3 installed.

### Data models

News
```json
{
   "id":1,
   "created_date":"2019-11-18 22:49:06.885453",
   "modified_date":"2019-11-18 22:49:06.885453",
   "title":"News title",
   "content":"News content"   
}
```

Comment
```json
{
   "id":1,
   "created_date":"2019-11-18 22:49:06.885453",
   "modified_date":"2019-11-18 22:49:06.885453",   
   "content":"Comment content"
}
```

### API
```bash
GET|POST http://localhost:8080/news/
GET|PUT|DELETE http://localhost:8080/news/:id/

GET|POST http://localhost:8080/news/:news_id/comments/
GET|PUT|DELETE http://localhost:8080/news/:news_id/comments/:id/
```

### Run
```bash
# create database
./db/create_db.sh

# run server
python start_server.py
```

### Usage examples
```bash
curl -X POST -d '{"title": "News title", "content": "News content"}' "http://localhost:8080/news/"
curl -X GET "http://localhost:8080/news/"
curl -X PUT -d '{"title": "News updated title", "content": "News updated content"}' "http://localhost:8080/news/1/"
curl -X DELETE "http://localhost:8080/news/1/"

curl -X POST -d '{"content": "Comment"}' "http://localhost:8080/news/1/comments/"
curl -X GET "http://localhost:8080/news/1/comments/"
curl -X PUT -d '{"content": "Updated comment"}' "http://localhost:8080/news/1/comments/1/"
curl -X DELETE "http://localhost:8080/news/1/comments/1/"
```

### Tests
```bash
python -m unittest discover -s news_restapi -p tests.py
```