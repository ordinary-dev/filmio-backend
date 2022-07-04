""" The module responsible for working with photos """

import hashlib
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
from pydantic import BaseModel

from .auth import get_current_user
from .mongo import photos
from .users import User

photos_router = APIRouter(tags=['photos'])


class Photo(BaseModel):
    hash: str
    original_extension: str
    width: int
    height: int


def get_extension(file_type: str) -> str:
    """
    Converts mime type to file extension.
    May be used to check if file type is supported or not.

    Returns:
    - `str` - file extension depending on the mime type
    - `None` - file format is not supported
    """
    if file_type == 'image/jpeg':
        return 'jpg'
    if file_type == 'image/png':
        return 'png'
    return None


@photos_router.post("/photos/", response_model=Photo)
async def upload_photo(file: UploadFile, current_user: User = Depends(get_current_user)) -> Photo:
    """
    Saves photo and returns photo width, height, extension and hash

    Returns:
    - `Photo` - hash, extension, width and height of the photo

    Raises:
    - `HTTPException` if file type is not supported
    """

    extension = get_extension(file.content_type)
    # Check if content type supported
    if not extension:
        raise HTTPException(status_code=400, detail="Unknown file type")

    # Get file hash
    file_hash = hashlib.sha1()
    while content := await file.read(1024):
        file_hash.update(content)

    # Create directory to store uploaded photos
    if not os.path.isdir('photos'):
        os.mkdir('photos')

    # Check if file was already uploaded
    hash_string = file_hash.hexdigest()
    if not os.path.isdir(f'photos/{hash_string}'):
        # Write file to disk
        await file.seek(0)
        os.mkdir(f'photos/{hash_string}')
        with open(f'photos/{hash_string}/original.{extension}', 'wb') as output_file:
            while content := await file.read(1024):
                output_file.write(content)
        await file.close()

        # Write info to database
        img = Image.open(f'photos/{hash_string}/original.{extension}')
        width, height = img.size
        photo = Photo(
            hash=hash_string,
            original_extension=extension,
            width=width,
            height=height
        )
        photos.insert_one(photo.dict())

    photo = Photo(**photos.find_one({'hash': hash_string}))
    return photo


@photos_router.get('/photos/{file_hash}/content', response_class=FileResponse)
async def get_file(file_hash: str) -> FileResponse:
    """
    Get a photo.

    Raises:
    - `HTTPException` - file was not found
    """
    photo = photos.find_one({'hash': file_hash})
    if not photo:
        raise HTTPException(
            status_code=404, detail="File was not found in database")
    file_src = f'photos/{file_hash}/original.{photo["original_extension"]}'
    if not os.path.isfile(file_src):
        print(file_src)
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_src)


@photos_router.get('/photos/{file_hash}/info', response_model=Photo)
async def get_photo_info(file_hash: str) -> Photo:
    """
    Returns the height, width, and format of a photo

    Raises:
    - `HTTPException` - file was not found
    """
    photo = photos.find_one({'hash': file_hash})
    if not photo:
        raise HTTPException(
            status_code=404, detail="File was not found in database")
    return Photo(**photo)
