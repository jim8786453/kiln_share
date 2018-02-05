import base64
import cStringIO

from eve.io.mongo.media import GridFSMediaStorage
from flask import current_app, abort
from PIL import Image


class GridFSImageStorage(GridFSMediaStorage):

    def put(self, content, filename=None, content_type=None, resource=None):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            # Resize to a maxiumum of 2048x2048.
            size = 2048, 2048

            # Convert contents to Image object.
            image_string = content.read()
            buffer_ = cStringIO.StringIO(image_string)
            image = Image.open(buffer_)

            # Run the thumbnailing.
            image.thumbnail(size)

            # Convert Image object back to contents.
            buffer_ = cStringIO.StringIO()
            image.save(buffer_, format="JPEG")
            content = buffer_.getvalue()

        return self.fs(resource).put(content, filename=filename,
                                     content_type=content_type)
