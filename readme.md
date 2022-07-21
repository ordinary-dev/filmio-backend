# Film.io
Backend server for `Film.io` created with FastAPI and MongoDB.

## Configuration
This project uses `python-decouple`.
You can save settings in environment variables or in `settings.ini` and `.env` files.
Example of `.env` file:
```
MONGODB_HOST=192.168.0.2
MONGODB_PORT=27017
SECRET_KEY=somethingrandom
```

## How to run
Make sure the database is running,
and the server address and port are specified in the settings.

* For development
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn filmio.main:app --reload
```

* For development (using docker-compose):
```
docker-compose -f docker-dev.yml up --build
```

* For production:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn filmio.main:app
```

* For production (using docker-compose):
```
docker-compose -f docker-prod.yml up --build
```

## Routes
---
### Users

* `POST /users`

Create a new user.

| Name          | Location | Type | Required? |
| ---           | ---      |---   | ---       |
| username      | body     | str  | true      |
| email         | body     | str  | true      |
| password      | body     | str  | true      |
| name          | body     | str  | false     |

Request:
```
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "email": "m@e.com", "password": "pass"}' \
     "http://api.filmio/users"
```

Response:
```JSON
{
    "username": "string",
    "email": "string",
    "name": "string"
}
```

* `GET /users/{username}`

Get information about user.

| Name          | Location | Type | Required? |
| ---           | ---      |---   | ---       |
| username      | query    | str  | true      |

Request:
```
curl "http://api.filmio/users/{username}"
```

Response:
```JSON
{
    "username": "string",
    "name": "string"
}
```

* `POST /token`

Get access token (JWT).

| Name          | Location | Type | Required? |
| ---           | ---      |---   | ---       |
| username      | body     | str  | true      |
| password      | body     | str  | true      |

Request:
```
curl -X 'POST' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=user&password=pass' \
     'http://api.filmio/token'
```

Response:
```JSON
{
  "access_token": "string",
  "token_type": "bearer"
}
```

* `GET /me`

Returns information about current user.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| Authorization | header   | bearer | true      |

Request:
```
curl -H 'Authorization: Bearer {token}' \
     'http://api.filmio/me'
```

Response:
```JSON
{
    "username": "string",
    "email": "string",
    "name": "string"
}
```

---
### Posts

* `POST /photos`

Upload a new photo.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| Authorization | header   | bearer | true      |
| file          | body     | file   | true      |

Request:
```
curl -X 'POST' \
     -H 'Authorization: Bearer {token}' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@{image.jpg}' \
     'http://api.filmio/photos/'
```

Response:
```JSON
{
    "hash": "string",
    "original_extension": "string",
    "width": 0,
    "height": 0
}
```

* `GET /photos/{hash}/content`

Get a photo.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| hash          | query    | string | true      |

Request:
```
curl 'http://api.filmio/photos/{hash}/content'
```

Response: image

* `GET /photos/{hash}/info`

Get information about photo (width, height, extension)

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| hash          | query    | string | true      |

Request:
```
curl 'http://api.filmio/photos/{hash}/info'
```

Response:
```JSON
{
  "hash": "string",
  "original_extension": "string",
  "width": 0,
  "height": 0
}
```

* `POST /posts`

Create a new post.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| Authorization | header   | bearer | true      |
| photo_id      | body     | string | true      |
| title         | body     | string | false     |
| description   | body     | string | false     |
| place         | body     | string | false     |

Request:
```
curl -X 'POST' \
     -H 'Authorization: Bearer {token}' \
     -H 'Content-Type: application/json' \
     -d '{"photo_id": "string", "title": "string", "description": "string", "place": "string"}' \
     'http://api.filmio/posts'
```

Response:
```JSON
{
  "title": "string",
  "description": "string",
  "place": "string",
  "photo_id": "string",
  "author": "string",
  "timestamp": 0
}
```

* `GET /posts/random`

Get random post.

Request:
```
curl 'http://api.filmio/posts/random'
```

Response:
```JSON
{
  "title": "string",
  "description": "string",
  "place": "string",
  "photo_id": "string",
  "author": "string",
  "timestamp": 0
}
```

* `GET /users/{username}/posts`

Get all posts from @username.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| username      | query    | string | true      |

Request:
```
curl http://api.filmio/users/{username}/posts
```

Response:
```JSON
["string"]
```

* `GET /users/{username}/posts/count`

Get the number of posts.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| username      | query    | string | true      |

Request:
```
curl http://api.filmio/users/{username}/posts/count
```

Response:
```JSON
0
```

* `GET /posts/location/{location}`

Get a list of posts with a given location.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| location      | query    | string | true      |

Request:
```
curl 'http://api.filmio/posts/location/{location}'
```

Response:
```JSON
[
  {
    "title": "string",
    "description": "string",
    "place": "string",
    "photo_id": "string",
    "author": "string",
    "timestamp": 0
  }
]
```

* `GET /posts/{id}`

Get information about post.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| id            | query    | string | true      |

Request:
```
curl 'http://api.filmio/posts/{id}'
```

Response:
```JSON
{
  "title": "string",
  "description": "string",
  "place": "string",
  "photo_id": "string",
  "author": "string",
  "timestamp": 0
}
```

* `PUT /posts/{id}`

Update information about post.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| id            | query    | string | true      |
| Authorization | header   | bearer | true      |
| title         | body     | string | false     |
| description   | body     | string | false     |
| place         | body     | string | false     |

Request:
```
curl -X 'PUT' \
     -H 'Authorization: Bearer {token}' \
     -H 'Content-Type: application/json' \
     -d '{"title": "string", "description": "string", "place": "string"}' \
     'http://api.filmio/posts/{id}'
```

* `DELETE /posts/{id}`

Delete a post.

| Name          | Location | Type   | Required? |
| ---           | ---      | ---    | ---       |
| id            | query    | string | true      |
| Authorization | header   | bearer | true      |

Request:
```
curl -X 'DELETE' \
     -H 'Authorization: Bearer {token}' \
     'http://api.filmio/posts/{id}'
```
