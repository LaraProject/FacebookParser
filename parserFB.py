import json
import re
import ftfy
import unidecode

class Parser:
    dataRaw = {}
    conversations = {}
    speakers = {}
    delayBetween2Conv = 0
    nbMessages = 0
    
    def __init__(self, fileName, nbMessages, delayBetween2Conv, withTimestamp=True):
        print('Parser launching...')

        self.delayBetween2Conv = delayBetween2Conv
        self.withTimestamp = withTimestamp

        with open(fileName) as json_file:
            self.dataRaw = json.load(json_file)

        self.nbMessages = min(nbMessages,len(self.dataRaw['messages']))

    def start(self):
            self.speakers['speakers'] = []
            self.conversations['speakers'] = []
            self.conversations['messages'] = []
            
            #Storing speaker's names
            for p in self.dataRaw['participants']:
                self.speakers['speakers'].append(p['name'])
                self.conversations['speakers'].append(p['name'])

            conversationId = 0
            timestamp = 0

            # Sort messages according to their timestamp
            self.dataRaw['messages'].sort(key=self.extract_time)

            #Get first timestamp
            while timestamp == 0:
                #Test if the current entry is a message (if not, the script below returns an error)
                try:
                    if self.withTimestamp:
                        self.conversations['messages'].append({
                            'sender_name': self.dataRaw['messages'][0]['sender_name'],
                            'content': self.cleanMessage(self.dataRaw['messages'][0]['content']),
                            'timestamp': self.dataRaw['messages'][0]['timestamp_ms'],
                            'conversationId': conversationId
                        })
                    else:
                        self.conversations['messages'].append({
                            'sender_name': self.dataRaw['messages'][0]['sender_name'],
                            'content': self.cleanMessage(self.dataRaw['messages'][0]['content']),
                            'conversationId': conversationId
                        })

                    timestamp = int(self.dataRaw['messages'][0]['timestamp_ms'])
                except:
                    pass
                
            #Storing and detecting conversations
            for k in range(1, self.nbMessages):
                try:
                    if abs(int(self.dataRaw['messages'][k]['timestamp_ms']) - timestamp) > self.delayBetween2Conv: 
                        conversationId += 1

                    #Update timestamp
                    timestamp = int(self.dataRaw['messages'][k]['timestamp_ms'])
                    
                    if self.withTimestamp:
                        self.conversations['messages'].append({
                            'sender_name': self.dataRaw['messages'][k]['sender_name'],
                            'content': self.cleanMessage(self.dataRaw['messages'][k]['content']),
                            'timestamp': self.dataRaw['messages'][k]['timestamp_ms'],
                            'conversationId': conversationId
                        })
                    else:
                        self.conversations['messages'].append({
                            'sender_name': self.dataRaw['messages'][k]['sender_name'],
                            'content': self.cleanMessage(self.dataRaw['messages'][k]['content']),
                            'conversationId': conversationId
                        })
                except:
                    pass

            print(self.conversations)
            #print(self.speakers)

    #Cleaning message method
    def cleanMessage(self, message):
        messageCleaned = ftfy.fix_text(message)
        messageCleaned = unidecode.unidecode(messageCleaned)
        messageCleaned = messageCleaned.lower()
        messageCleaned = re.sub(r"[-()^\"#/@;:<>{}`+=~|.!?,]", "", messageCleaned)

        #print(messageCleaned)
        
        return messageCleaned

    # Get the timestamp
    def extract_time(self, msg):
        try:
            return int(msg['timestamp_ms'])
        except KeyError:
            return 0

    #Export the final .json file
    def finalDump(self, filename):
        with open(filename, 'w') as outfile:
            json.dump(self.conversations, outfile)


#---------------------------------

#Settings            
delayBetween2Conv = 50000 #in milliseconds
nbMessages = 100
fbConvFilename = 'conversation_LouisRiad.json'

#Parser launching...
parser = Parser(fbConvFilename, nbMessages, delayBetween2Conv)
parser.start()