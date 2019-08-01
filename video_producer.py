import sys
import time
import cv2
from kafka import KafkaProducer
import argparse
import uuid
import json
import pickle

topic = "distributed-video1"

parser = argparse.ArgumentParser(description='Kafka Video Producer')

parser.add_argument('-v', '--video',
                    dest='video',
                    type=str,
                    default="")
args = parser.parse_args()

device_id = str(uuid.uuid4())


def publish_video(video_file):
    """
    Publish given video file to a specified Kafka topic.
    Kafka Server is expected to be running on the localhost. Not partitioned.

    :param video_file: path to video file <string>
    """
    # Start up producer
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    # Open file
    video = cv2.VideoCapture(video_file)

    print('publishing video...')

    while video.isOpened():
        success, frame = video.read()

        # Ensure file was read successfully
        if not success:
            print("bad read!")
            break

        # Convert image to png
        ret, buffer = cv2.imencode('.jpg', frame)

        obj = {
            'deviceId': device_id,
            'frame': buffer.tobytes()
        }

        # Convert to bytes and send to kafka
        producer.send(topic, pickle.dumps(obj))

        time.sleep(0.2)
    video.release()
    print('publish complete')


def publish_camera():
    """
    Publish camera video stream to specified Kafka topic.
    Kafka Server is expected to be running on the localhost. Not partitioned.
    """

    # Start up producer
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    camera = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = camera.read()

            ret, buffer = cv2.imencode('.jpg', frame)

            obj = {
                'deviceId': device_id,
                'frame': buffer.tobytes()
            }

            producer.send(topic, pickle.dumps(obj))

            # Choppier stream, reduced load on processor
            time.sleep(0.2)
    except:
        print("\nExiting.")
        sys.exit(1)
    finally:
        camera.release()


if __name__ == '__main__':
    """
    Producer will publish to Kafka Server a video file passed as argument. 
    Otherwise it will default by streaming webcam feed.
    """

    video_path = args.video
    if not video_path:
        print("publishing feed!")
        publish_camera()
    else:
        publish_video(video_path)
