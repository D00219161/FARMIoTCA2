# Initial code adapted from https://github.com/pahowart/ampread/blob/master/ampread_python3e.py

import re
import sys
import datetime
import time
import Adafruit_ADS1x15
import math

# from pubnub.callbacks import SubscribeCallback
# from pubnub.enums import PNStatusCategory, PNOperationType
# from pubnub.pnconfiguration import PNConfiguration
# from pubnub.pubnub import PubNub
#
# pnconfig = PNConfiguration()
# pnconfig.cipher_key = 'myCipherKey'
# pnconfig.auth_key = 'Homesafe-Matthew-Raspberry-Pi'
# pnconfig.subscribe_key = 'sub-c-12924b4c-2f48-11eb-9713-12bae088af96'
# pnconfig.publish_key = 'pub-c-4c71c151-b075-498f-bfbc-c6f3221ed3b6'
# pnconfig.uuid = '8f255df0-3657-11eb-adc1-0242ac120002'
# pubnub = PubNub(pnconfig)


# Create a second ADS1015 ADC instance if are using a second ADC.
adc2 = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=1)

GAIN_A = 4  # see ads1015/1115 documentation for potential values.
GAIN_B = 4
samples = 100  # increase or decrease # of samples taken from ads1015
places = int(2)  # set rounding
time_elapsed = (0)

# start loop to find current and utility voltage and then upload to influxdb
while True:

    try:
        # reset variables before reading adc2
        count = int(0)
        data = [0] * 4
        maxValue = [0] * 4
        IrmsB = [0] * 4
        ampsB = [0] * 4

        # need to get the peak voltage from each input and use root mean square formula (RMS)
        # this loop will take 200 samples from each input and give you the highest (peak) voltage
        while count < samples:
            count += 1
            # nested loop to find highest sensor values from samples
            for i in range(0, 4):

                # read input A0 from adc2 as absolute value
                data[i] = abs(adc2.read_adc(i, gain=GAIN_B))

                # see if you have a new maxValue
                if data[i] > maxValue[i]:
                    maxValue[i] = data[i]

            # convert maxValue sensor outputs to amps
            # I used a sct-013 that is calibrated for 1000mV output @ 20A. Usually has 20A/1V printed on it.
            for i in range(0, 4):
                IrmsB[i] = float(maxValue[i] / float(22000) * 20)
                IrmsB[i] = round(IrmsB[i])
                ampsB[i] = IrmsB[i] / math.sqrt(2)  # RMS formula to get current reading to match what an ammeter shows.
                ampsB[i] = round(ampsB[i])

        # assign range value to variable
        ampsB0 = ampsB[0]
        print("AMPS READING:")
        print (ampsB0)

        print("KILOWATTS:")
        kilowatts = ((ampsB0) * 230 / 1000)
        print(kilowatts)

    except KeyboardInterrupt:
        print('You cancelled the operation.')
        sys.exit()

# def publish(custom_channel, msg):
#     pubnub.publish().channel(custom_channel).message(msg).pn_async(my_publish_callback)
#
#
# def my_publish_callback(envelope, status):
#     # Check whether request successfully completed or not
#     if not status.is_error():
#         pass  # Message successfully published to specified channel.
#     else:
#         pass  # Handle message publish error. Check 'category' property to find out possible issue
#         # because of which request did fail.
#         # Request can be resent using: [status retry];
#
#
# class MySubscribeCallback(SubscribeCallback):
#     def presence(self, pubnub, presence):
#         pass  # handle incoming presence data
#
#     def status(self, pubnub, status):
#         if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
#             pass  # This event happens when radio / connectivity is lost
#
#         elif status.category == PNStatusCategory.PNConnectedCategory:
#             # Connect event. You can do stuff like publish, and know you'll get it.
#             # Or just use the connected event to confirm you are subscribed for
#             # UI / internal notifications, etc
#             pubnub.publish().channel(myChannel).message('Connected to PubNub').pn_async(my_publish_callback)
#         elif status.category == PNStatusCategory.PNReconnectedCategory:
#             pass
#             # Happens as part of our regular operation. This event happens when
#             # radio / connectivity is lost, then regained.
#         elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
#             pass
#             # Handle message decryption error. Probably client configured to
#             # encrypt messages and on live data feed it received plain text.
#
#     def message(self, pubnub, message):
#         # Handle new message stored in message.message
#         try:
#             print(message.message)
#             msg = message.message
#             key = list(msg.keys())
#             if key[0] == "event":       #{"event" : {"sensor_name" : True}}
#                 self.handleEvent(msg)
#         except Exception as e:
#             print("Received: ", message.message)
#             print(e)
#             pass
#
#
#     def handleEvent(self, msg):
#         global data
#         eventData = msg["event"]
#         key = list(eventData.keys())
#         if key[0] in sensorList:
#             if eventData[key[0]] is True:
#                 data["alarm"] = True
#             elif eventData[key[0]] is False:
#                 data["alarm"] = False
#
#
# if __name__ == "__main__":
#     sensorsThread = threading.Thread(target=motionDetection)
#     sensorsThread.start()
#     pubnub.add_listener(MySubscribeCallback())
#     pubnub.subscribe().channels(myChannel).execute()
