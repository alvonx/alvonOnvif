import math
import time
from threading import Thread

import cv2
import numpy as np


class Stream:
    def __init__(self, LOGGER, EXTRAS, media_sources):
        self.LOGGER = LOGGER
        self.EXTRAS = EXTRAS
        n = len(media_sources)
        self.sources = [x for x in media_sources]  # clean source names for later
        self.imgs, self.fps, self.frames, self.threads = [None] * n, [0] * n, [0] * n, [None] * n
        for source_idx, (cam_id, media_url) in enumerate(media_sources):
            self.cam_id = cam_id
            self.media_url = media_url
            cap_stream = cv2.VideoCapture(self.media_url)
            assert cap_stream.isOpened(), f"Failed to open {self.media_url}"
            # media_width = int(self.cap_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            # media_height = int(self.cap_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap_stream.get(cv2.CAP_PROP_FPS)
            self.frames[source_idx] = max(int(cap_stream.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')
            self.fps[source_idx] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30
            _, self.imgs[source_idx] = cap_stream.read()  # guarantee first frame
            self.threads[source_idx] = Thread(target=self.update, args=([source_idx, cap_stream, self.media_url]), daemon=True)
            self.threads[source_idx].start()

    def update(self, i, cap, stream):
        n, f = 0, self.frames[i]  # frame number, frame array
        while cap.isOpened() and n < f:
            n += 1
            success, im = cap.read()
            if success:
                self.imgs[i] = im
            else:
                self.LOGGER.warning('WARNING Video stream unresponsive, please check your IP camera connection.')
                self.EXTRAS.print_color('red', 'Video stream unresponsive.... checking reconnection....')
                # self.imgs[i] = np.zeros_like(self.imgs[i])
                cap.open(stream)  # re-open stream if signal was lost

    def __iter__(self):
        self.count = -1
        return self

    def __next__(self):
        self.count += 1
        if not all(x.is_alive() for x in self.threads) or cv2.waitKey(1) == ord('q'):  # q to quit
            cv2.destroyAllWindows()
            raise StopIteration

        im0 = self.imgs.copy()
        return self.cam_id, im0

    def __len__(self):
        return len(self.sources)
