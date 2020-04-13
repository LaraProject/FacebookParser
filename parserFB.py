import json
import re
import ftfy
import unidecode


class Parser:

    dataRaw = {}
    conversations = {}
    speakers = {}
    conv_blacklist = []
    delayBetween2Conv = 0
    nbMessages = 0

    def __init__(self, fileName, nbMessages, delayBetween2Conv, withTimestamp=True):
        print('Parser launching...')

        self.delayBetween2Conv = delayBetween2Conv
        self.withTimestamp = withTimestamp

        with open(fileName) as json_file:
            self.dataRaw = json.load(json_file)

        self.nbMessages = min(nbMessages, len(self.dataRaw['messages']))

    def start(self):
        self.speakers['speakers'] = []
        self.conversations['speakers'] = []
        self.conversations['messages'] = []

        # Storing speaker's names
        for p in self.dataRaw['participants']:
            self.speakers['speakers'].append(p['name'])
            self.conversations['speakers'].append(p['name'])

        conversationId = 0
        subConversationId = 0
        lastSender = ""
        timestamp = 0

        # Sort messages according to their timestamp
        self.dataRaw['messages'].sort(key=self.extract_time)

        # Get first timestamp
        while timestamp == 0:
            # Test if the current entry is a message (if not, the script below returns an error)
            try:
                msg = self.getMsg(0, 0, 0)
                if not (msg == None):
                    self.conversations['messages'].append(msg)
                timestamp = int(self.dataRaw['messages'][0]['timestamp_ms'])
                lastSender = self.dataRaw['messages'][0]['sender_name']
            except:
                print("paserFB: Initialize with the " + str(k) + "-th message.")

        # Storing and detecting conversations
        for k in range(1, self.nbMessages):
            try:
                # Get the number of the conversation
                if abs(int(self.dataRaw['messages'][k]['timestamp_ms']) - timestamp) > self.delayBetween2Conv:
                    conversationId += 1
                    subConversationId = 0

                # Update timestamp
                timestamp = int(self.dataRaw['messages'][k]['timestamp_ms'])

                # Update subconversation id
                if (lastSender != self.dataRaw['messages'][k]['sender_name']):
                    lastSender = self.dataRaw['messages'][k]['sender_name']
                    subConversationId += 1

                # Add message to the list
                next_msg = self.getMsg(k, conversationId, subConversationId)
                if not (next_msg == None):
                    self.conversations['messages'].append(next_msg)
            except:
                print("parserFB: Problem when storing the " + str(k) + "-th message.")

        # Apply the blacklist
        self.applyBlacklist()

        # print(self.conversations)
        # print(self.speakers)

    # Remove any conversation from the blacklist
    def applyBlacklist(self):
        self.conversations['messages'] = [x for x in self.conversations['messages'] if x['conversationId'] not in self.conv_blacklist]

    # Get k-th message
    def getMsg(self, k, conversationId, subConversationId):
        try:
            if self.withTimestamp:
                msg = {
                    'sender_name': self.dataRaw['messages'][k]['sender_name'],
                    'content': self.cleanMessage(self.dataRaw['messages'][k]['content']),
                    'timestamp': self.dataRaw['messages'][k]['timestamp_ms'],
                    'conversationId': conversationId,
                    'subConversationId': subConversationId
                }
            else:
                msg = {
                    'sender_name': self.dataRaw['messages'][k]['sender_name'],
                    'content': self.cleanMessage(self.dataRaw['messages'][k]['content']),
                    'conversationId': conversationId,
                    'subConversationId': subConversationId
                }
            return msg
        except:
            print("paserFB: Impossible to get the " + str(k) + "-th message")
            # Add this conversation to the blacklist
            self.conv_blacklist.append(conversationId)
            return None

    # Cleaning message method
    def cleanMessage(self, message):
        messageCleaned = ftfy.fix_text(message)
        messageCleaned = unidecode.unidecode(messageCleaned)
        messageCleaned = messageCleaned.lower()
        # messageCleaned = re.sub(r"[-()^\"#/@;:<>{}`+=~|.!?,]", '', messageCleaned)

        # print(messageCleaned)
        return messageCleaned

    # Get the timestamp
    def extract_time(self, msg):
        try:
            return int(msg['timestamp_ms'])
        except KeyError:
            return 0

    # Export the final .json file
    def finalDump(self, filename):
        with open(filename, 'w') as outfile:
            json.dump(self.conversations, outfile)


# ---------------------------------

# Settings
 
delayBetween2Conv = 50000  # in milliseconds
nbMessages = 100
fbConvFilename = 'conversation_LouisRiad.json'

# Parser launching...

parser = Parser(fbConvFilename, nbMessages, delayBetween2Conv)
parser.start()
