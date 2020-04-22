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

	def __init__(self, fileName, nbMessages, delayBetween2Conv, withTimestamp=True, debug=False):
		self.debug = debug

		if self.debug:
			print('Parser launching...')

		self.delayBetween2Conv = delayBetween2Conv
		self.withTimestamp = withTimestamp
		self.debug = debug

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

		lastSender = ""
		timestamp = 0

		# Sort messages according to their timestamp
		self.dataRaw['messages'].sort(key=self.extract_time)

		# Get first timestamp
		k = 0
		while (timestamp == 0) and (k < len(self.dataRaw['messages'])):
			# Test if the current entry is a message (if not, the script below returns an error)
			msg = self.getMsg(k, 0, 0)
			if not (isinstance(msg, int)):
				self.conversations['messages'].append(msg)
				timestamp = int(self.dataRaw['messages'][k]['timestamp_ms'])
				lastSender = self.dataRaw['messages'][k]['sender_name']
			k += 1

		# Storing and detecting conversations
		conversationId = 0
		subConversationId = 0
		ignoreConversation = -1
		for k in range(1, self.nbMessages):
			# Get the number of the conversation
			if abs(int(self.dataRaw['messages'][k]['timestamp_ms']) - timestamp) > self.delayBetween2Conv:
				# Check if the previous conversation was a monologue
				if (len(self.conversations['messages']) > 0) and (self.conversations['messages'][-1]['subConversationId'] == 0):
					self.removeConv(conversationId)
				conversationId += 1
				if (lastSender != self.dataRaw['messages'][k]['sender_name']):
					subConversationId = -1
				else:
					subConversationId = 0
				ignoreConversation = -1

			# Ignore some conversation
			if (conversationId == ignoreConversation):
				continue

			# Update timestamp
			timestamp = int(self.dataRaw['messages'][k]['timestamp_ms'])

			# Update subconversation id
			if (lastSender != self.dataRaw['messages'][k]['sender_name']):
				lastSender = self.dataRaw['messages'][k]['sender_name']
				subConversationId += 1

			# Add message to the list
			next_msg = self.getMsg(k, conversationId, subConversationId)
			# Remove conversations contaning invalid messages
			if (isinstance(next_msg, int)):
				self.removeConv(conversationId)
				ignoreConversation = conversationId
			else:
				self.conversations['messages'].append(next_msg)

	# Remove a conversation after it got added
	def removeConv(self, conv_id):
		found_conversation = False
		for conv in range(len(self.conversations['messages'])-1,-1,-1):
			if (self.conversations['messages'][conv]['conversationId'] == conv_id):
				found_conversation = True
				del self.conversations['messages'][conv]
			elif found_conversation:
				break


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
			if self.debug:
				print("paserFB: Impossible to get the " + str(k) + "-th message")
			# Report this message as invalid
			return conversationId

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

	# Get the number of conversations
	def getNbConversation(self):
		return len(self.conversations['messages'])

	# Export the final .json file
	def finalDump(self, filename):
		if self.debug:
			print('Dumping ...')
		with open(filename, 'w') as outfile:
			json.dump(self.conversations, outfile)


# Find the optimal interval between conversations
def optimalInterval(fbConvFilename, nbMessages, step_ms, min_duration_ms, max_duration_ms, details=False):
	data = []
	best = (-1,9223372036854775807)
	for delay in range(min_duration_ms,max_duration_ms,step_ms):
		print("optimalInterval: Testing delay=" + str(delay/(60*1000)) + " min")
		parser = Parser(fbConvFilename, nbMessages, delay, False, False)
		parser.start()
		length = parser.getNbConversation()
		if details:
			# Remenber the data for analysis
			data.append((delay,length))
		print("optimalInterval: Length of " + str(length))
		if (length < best[1]):
			best = (delay,length)
	if details:
		print(data)
	return best[1]

# Get the number of messages per day
import datetime
import matplotlib.pyplot as plt
def msgPerDay(filenames, exportData=False, noGraphics=False, forceDates=None):
	# Import all timestamps
	timestamps = []
	for filename in filenames:
		with open(filename) as json_file:
			dataRaw = json.load(json_file)
			timestamps += [datetime.datetime.fromtimestamp(float(msg['timestamp_ms'])/1000.) for msg in dataRaw['messages']]
	timestamps = sorted(set(timestamps))
	if forceDates != None:
		min_date, max_date = forceDates
	else:
		min_date, max_date = min(timestamps).replace(hour=0, minute=0, second=0, microsecond=0), max(timestamps).replace(hour=0, minute=0, second=0, microsecond=0)
	print("From " + min(timestamps).strftime("%d/%m/%Y") + " to "  + max(timestamps).strftime("%d/%m/%Y"))
	# Add the data in a dictionnary
	res = {}
	length = 0
	for msg in timestamps:
		cur_day = msg.replace(hour=0, minute=0, second=0, microsecond=0)
		if (min_date <= cur_day <= max_date):
			length += 1
			if cur_day not in res:
				res[cur_day] = 0
			else:
				res[cur_day] += 1
	# Give some statistics
	print(str(length) + " messages.")
	# Add missing dates
	cur_date = min_date
	while cur_date <= max_date:
		cur_day = cur_date.replace(hour=0, minute=0, second=0, microsecond=0)
		if cur_day not in res:
			res[cur_day] = 0
		cur_date += datetime.timedelta(days=1)
	# Prepare matplotlib
	if not noGraphics:
		lists = sorted(res.items())
		X, Y = zip(*lists)
		# Plot everything
		plt.plot(X, Y)
		plt.xticks(rotation='vertical')
		plt.show()
	return X,Y

# ---------------------------------

# Settings
 
delayBetween2Conv = 60 * 1000 * 20  # 20 mins of interval
nbMessages = 50000 # 50 000 messages
debug = False # debugging is disabled
withTimestamp = False # disable timestamps
fbConvFilename = 'fb_benjamin.js'

# Parser launching...

parser = Parser(fbConvFilename, nbMessages, delayBetween2Conv, withTimestamp, debug)
parser.start()
