import time

import pymongo
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .auth import get_current_user
from .mongo import photos, posts
from .users import User

posts_router = APIRouter(tags=['posts'])


class Post(BaseModel):
    photo_id: str
    title: str | None = None
    description: str | None = None
    place: str | None = None


class PostInDB(Post):
    author: str
    timestamp: int


class PostOut(PostInDB):
    pass


@posts_router.post('/posts', response_model=PostOut)
async def save_new_post(post: Post, user: User = Depends(get_current_user)):
    """
    Store the new post in the database.

    Returns:
    - `Post` - original post if the number of posts does not exceed the maximum allowed

    Raises:
    - `HTTPException` - the maximum number of posts has been exceeded
    """

    # Count existing posts
    if posts.count_documents({'author': user.username}) >= 36:
        raise HTTPException(status_code=400, detail='Too much posts')

    # Save post
    post_in_db = PostInDB(
        **post.dict(), author=user.username, timestamp=int(time.time()))
    posts.insert_one(post_in_db.dict())
    return post_in_db


@posts_router.get('/posts/random', response_model=PostOut)
async def get_random_post() -> PostOut:
    """
    Returns a random post
    """
    post = posts.aggregate([{"$sample": {"size": 1}}]).next()
    return PostOut(**post)


@posts_router.get('/users/{username}/posts', response_model=list[str])
async def get_posts(username: str):
    """ Returns all posts by a specific user """
    posts_from_db = posts.find({'author': username}).sort(
        'timestamp', pymongo.DESCENDING)
    return [post['photo_id'] for post in posts_from_db]


@posts_router.get('/users/{username}/posts/count', response_model=int)
async def get_posts_count(username: str) -> int:
    """ Returns the number of posts a @username has """
    return posts.count_documents({'author': username})


@posts_router.get('/posts/location/{location}', response_model=list[PostOut])
async def get_posts_by_location(location: str):
    """
    Get a list of posts with a given location
    """
    query = {'place': location}
    res = posts.find(query)
    return [PostOut(**post) for post in res]


@posts_router.get('/posts/{id}', response_model=PostOut)
async def get_one_post(id: str):
    """
    Get information about post

    Raises:
    - `HTTPException` - post was not found
    """
    query = {'photo_id': id}
    post = posts.find_one(query)
    if not post:
        raise HTTPException(404, 'Post was not found')
    return PostOut(**post)


@posts_router.put('/posts/{id}')
async def update_post(id: str, new_post: Post, user: User = Depends(get_current_user)):
    """
    Update information about post

    Raises:
    - `HTTPException` - post was not found, current user != author or photo_id was changed
    """
    query = {'photo_id': id}
    post = posts.find_one(query)
    if not post:
        raise HTTPException(404, 'Post was not found')
    post = PostInDB(**post)
    if post.author != user.username:
        raise HTTPException(400, 'You are not the author of the post')
    if post.photo_id != new_post.photo_id:
        raise HTTPException(400, "You can't change photo id")
    posts.update_one(query, { "$set": new_post.dict()})


@posts_router.delete('/posts/{id}')
async def delete_post(id: str, user: User = Depends(get_current_user)):
    """
    Delete one post by id

    Raises:
    - `HTTPException` - post was not found or current user != author
    """
    query = {'photo_id': id}
    post = posts.find_one(query)
    if not post:
        raise HTTPException(404, 'Post was not found')
    post = PostInDB(**post)
    if post.author != user.username:
        raise HTTPException(400, 'You are not the author of the post')
    posts.delete_one(query)
    return post
