import json
import argparse
import cv2

from controller import Controller


def main():
    print('OpenCV version: {}'.format(cv2.__version__))
    (major, minor, _) = cv2.__version__.split('.')
    assert major == '4' and minor == '1', 'OpenCV version must be 4.1'

    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_device', dest='video_device',
                        help='Video device # of USB webcam (/dev/video?) [0]',
                        default=0, type=int)
    arguments = parser.parse_args()
    video_device = arguments.video_device

    # Load env file
    env_path = './env.json'
    try:
        with open(env_path) as env_json:
            env = json.load(env_json)
    except IOError:
        print('Cannot open "source/frontend/env.json".\nCopy "default.env.json" file as a new file called "env.json" and edit parameters in it.')
        raise

    controller = Controller(env, video_device)
    controller.run()


if __name__ == '__main__':
    main()
