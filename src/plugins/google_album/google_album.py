from gphotospy import authorize
from gphotospy.media import *
from urllib.request import urlopen
from plugins.base_plugin.base_plugin import BasePlugin
from utils.image_utils import get_image
import logging
import time
import os
import logging

logger = logging.getLogger(__name__)

class GoogleAlbum(BasePlugin):
    CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "google_auth.json")

    def generate_image(self, settings, device_config):
        service = authorize.init(self.CLIENT_SECRET_FILE)
        media_manager = Media(service)

        album_id = "AItduvASV8Nh-9jA_M10xnNXt5oyuJP-n9Ss1wTPWgywfmF_OwH59uAWfUwtxvNge5ZaKxTsuDi5"
        last_updated_at = settings.get("images_cache_ts", time.time() - 25 * 60 * 60)
        image_ids = settings.get("images_ids", [])
        cached_index = settings.get("index", 0) + 1
        logger.info(f"Images last queried at {str(last_updated_at)}")
        if time.time() - last_updated_at > 1 * 60 * 60:
            album_media_list = list(media_manager.search_album(album_id))
            image_ids = [item.get("id") for item in album_media_list]
            if len(settings.get("images_ids", [])) != len(image_ids):
                cached_index = 0
            settings["images_ids"] = image_ids
            settings["images_cache_ts"] = time.time()

        cached_index = cached_index % len(image_ids)
        settings["index"] = cached_index
        logger.info(f"Loading image {str(cached_index)} from {str(len(image_ids))}")
        base_url = media_manager.get(image_ids[cached_index]).get("baseUrl")

        desired_width, desired_height = device_config.get_resolution()
        image_url = "{}=w{}-h{}".format(base_url, desired_width, desired_height)
        try:
            img = get_image(image_url)
        except Exception as e:
            logger.error(f"Failed to read image file: {str(e)}")
            raise RuntimeError("Failed to read image file.")

        return img
