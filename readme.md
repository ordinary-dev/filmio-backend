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
### Users
* `GET /users/{username}`

Returns information about user.
```JSON
{
    "username": "string",
    "name": "string",
    "profile_picture": "string"
}
```

* `GET /me`

Returns information about current user.

* `POST /users`

Create a new user.

* `POST /token`

Get JWT access token.

### Posts

* `POST /photos`

Upload a new photo.
```JSON
{
    "hash": "string",
    "original_extension": "string",
    "width": 0,
    "height": 0
}
```

* `GET /photos/{file_hash}/content`

Get a photo.

* `GET /photos/{file_hash}/info`

Get information about photo (width, height, extension)

* `POST /posts`

Create a new post.

* `GET /posts/random`

Get random post.

* `GET /users/{username}/posts`

Get all posts from @username.

* `GET /users/{username}/posts/count`

Get the number of posts.

* `PUT /posts/{id}`

Update information about post

* `DELETE /posts/{id}`

Delete a post