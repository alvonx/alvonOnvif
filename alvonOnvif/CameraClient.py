import configparser
import os
import sys
from onvif import ONVIFCamera

PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

STREAM = {
    'main': 0,
    'sub': 1
}


def available_capability(cap_detail):
    capability_set = set()
    for name in cap_detail:
        capability_set.add(name.lower())
    return capability_set


class Camera:
    def __init__(self, LOGGER, EXTRAS, camera_id, stream='main'):
        self.LOGGER = LOGGER
        self.EXTRAS = EXTRAS
        self.which_stream = stream
        self.snapshot_uri = None
        self.stream_uri = None
        self.profile_token = None
        self.__main_stream = None
        self.connected = False
        self.this_camera_id = camera_id
        config_obj = configparser.ConfigParser()
        config_file_path = os.path.join(PROJECT_PATH, 'config.ini')
        config_obj.read(f"{config_file_path}")
        box_config = config_obj['cam_info']
        CAMERA_HOST = box_config[f'cam_host_{self.this_camera_id}']
        CAMERA_PORT = box_config[f'cam_port_{self.this_camera_id}']
        CAMERA_USER = box_config[f'cam_user_{self.this_camera_id}']
        CAMERA_PASS = box_config[f'cam_pass_{self.this_camera_id}']
        self.cam_host = CAMERA_HOST
        self.cam_port = CAMERA_PORT
        self.cam_user = CAMERA_USER
        self.cam_pass = CAMERA_PASS
        try:
            self.__camera_onvif_obj = ONVIFCamera(CAMERA_HOST, CAMERA_PORT, CAMERA_USER, CAMERA_PASS)
        except Exception as error:
            # self.EXTRAS.exception_log_function(sys.exc_info(), f"Onvif object creation error: {error}")
            self.EXTRAS.print_color('red', f"Onvif object creation error: {error}", ret=False)
            self.LOGGER.error(f"onvif object not created {self.this_camera_id}")
            self.__camera_onvif_obj = None
        if self.__camera_onvif_obj is None:
            self.connected = False
        else:
            self.__device_mgmt_service = self.__camera_onvif_obj.create_devicemgmt_service()
            self.device_hostname = str(self.__device_mgmt_service.GetHostname().Name)
            self.device_information = self.__device_mgmt_service.GetDeviceInformation()

            self.__capabilities = available_capability(self.__device_mgmt_service.GetCapabilities({'Category': 'All'}))
            self.EXTRAS.print_color("yellow", f"capability => {self.__capabilities}", ret=False)

            # create services
            self.__media_service = self.__camera_onvif_obj.create_media_service()
            self.__recording_service = self.__camera_onvif_obj.create_recording_service() if 'recording' in self.__capabilities else None
            self.__analytics_service = self.__camera_onvif_obj.create_analytics_service()
            self.__events_service = self.__camera_onvif_obj.create_events_service()
            self.__pullpoint_service = self.__camera_onvif_obj.create_pullpoint_service()

            # connect to pull-point service
            self.__pullpoint_subscription = self.__events_service.CreatePullPointSubscription({'InitialTerminationTime': 'PT60S'})

            # get the stream
            self.__get_stream()
            self.__get_stream_uri()
            self.__get_snapshot_uri()

            # print(self.__media_service.GetVideoSources())
            # print(self.__media_service.GetRecordingSummary())

            print(self.__media_service.GetRecordingConfiguration())

    def __get_stream(self):
        try:
            get_all_profiles = self.__media_service.GetProfiles()
            for p in get_all_profiles:
                print(p.Name)
            self.__main_stream = get_all_profiles[STREAM.get(self.which_stream, 0)] if len(get_all_profiles) else None
            # self.profile_token = self.__main_stream.token if 'token' in self.__main_stream else self.__main_stream._token if '_token' in self.__main_stream else None
            self.profile_token = self.__main_stream.token if 'token' in self.__main_stream else None
            self.connected = True
        except Exception as error:
            self.EXTRAS.exception_log_function(sys.exc_info(), f"Connection error: {error}")
            self.connected = False

    def __get_stream_uri(self):
        if not self.connected:
            return ''
        try:
            stream_uri_info = self.__media_service.GetStreamUri({
                'StreamSetup': {
                    'Stream': 'RTP-Unicast',
                    'Transport': {
                        'Protocol': 'RTSP',
                    }
                },
                'ProfileToken': self.profile_token
            })
            stream_uri = str(stream_uri_info.Uri)
            stream_uri = stream_uri.replace('rtsp://', f'rtsp://{self.cam_user}:{self.cam_pass}@')
            self.stream_uri = stream_uri
        except Exception as error:
            self.EXTRAS.exception_log_function(f"Stream uri error: {error}")
            self.stream_uri = None

    def __get_snapshot_uri(self):
        if not self.connected:
            return ''
        try:
            snapshot_uri_info = self.__media_service.GetSnapshotUri({
                'ProfileToken': self.profile_token
            })
            snapshot_uri = str(snapshot_uri_info.Uri)
            snapshot_uri = snapshot_uri.replace('http://', f'http://{self.cam_user}:{self.cam_pass}@')
            self.snapshot_uri = snapshot_uri
        except Exception as error:
            self.EXTRAS.exception_log_function(f"Snapshot uri error: {error}")
            self.snapshot_uri = None
