import speech_recognition as sr
import paho.mqtt.client as mqtt
import argparse
import signal
import time

skill_one_cloud = ["skill one", "skill 1", "skil one", "skil 1", "one", "1", "still one", "stillwell", "still water"]
skill_two_cloud = ["skill two", "skill 2", "guity", "skill to", "skilled two", "skilled to", "skilled 2", "two", "to", "2", "skil to", "skil 2", "schooltube", "school 2", "school to"]
skill_three_cloud = ["skill three", "skill 3", "skills 3", "skills three", "skillz three", "skillz 3", "three", "3", "sklz 3"]

# MQTT related
def on_connect(client, userdata, flags, rc):
  print("Connection returned result: " + str(rc))

def on_disconnect(client, userdata, rc):
  if rc != 0:
    print('Unexpected Disconnect')
  else:
    print('Expected Disconnect')

# speech recog callback
def callback(recognizer, audio):
    #{'alternative': [{'transcript': 'skills 3', 'confidence': 0.81178844}, {'transcript': 'skills three'}, 
    #{'transcript': 'Skill 3'}, {'transcript': 'skill three'}, {'transcript': 'skills III'}], 'final': True}
    try:
        res_dict = recognizer.recognize_google(audio, show_all=True)
        print(res_dict)
        if isinstance(res_dict, list):
            return
        output = None

        predicted = []
        for transcript_dict in res_dict['alternative']:
            predicted.append(transcript_dict['transcript'])

        for each_predicted in predicted:
            if each_predicted.lower() in skill_one_cloud:
                output = 'skill 1'
                break
            elif each_predicted.lower() in skill_two_cloud:
                output = 'skill 2'
                break
            elif each_predicted.lower() in skill_three_cloud:
                output = 'skill 3'
                break
        
        if output != None:
            print(output)
            client.publish(topic, output, qos=1)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


if __name__ == '__main__':

    # get topic from input
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topic", type=str, required=True)
    args = parser.parse_args()
    global topic
    topic = args.topic

    # initialize mqtt client
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect_async('mqtt.eclipseprojects.io')
    client.loop_start()

    # register sigint to clear everything
    def signal_handler(sig, frame):
        stop_listening(wait_for_stop=False)
        client.loop_stop()
        client.disconnect()
        exit()
    signal.signal(signal.SIGINT, signal_handler)

    # initialize recognizers
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

    stop_listening = r.listen_in_background(m, callback, phrase_time_limit=2.0)

    # enter loop
    while True:
        time.sleep(10)
        
        
