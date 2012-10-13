# -*- coding: utf-8 -*-
from collections import defaultdict, Counter
import sys
import random

try:
	from botscript import BotScript
except ImportError:
	import sys
	sys.path.append("../")
	from botscript import BotScript

STOP_WORDS = """
se
on
kyl
ja
tai
ku
aika
hyvä
että
jees
""".split()


class Start:
	def __str__(self):
		return "[^]"


class End:
	def __str__(self):
		return "[$]"


class Bigram(object):
	@classmethod
	def _generate4(cls, words, start, words_sentence):
		sentence = [start]

		while sentence[-1] is not End:
			most_common = words[sentence[-1]].most_common()

			if len(most_common) < 2:
				break

			c = Counter()
			for word, weight in most_common:
				if word is End and len(sentence) < 20:
					continue
				else:
					for comp_word, comp_weight in words_sentence[word].most_common():
						if comp_word not in STOP_WORDS and comp_word in sentence:
							c[word] += comp_weight
					break

			try:
				sentence.append(c.most_common()[0][0])
			except IndexError:
				random.shuffle(most_common)
				word, weight = most_common.pop()
				sentence.append(word)

		if sentence[-1] is End:
			sentence = sentence[:-1]
		if sentence[0] is Start:
			sentence = sentence[1:]

		return sentence

	@classmethod
	def _generate3(cls, words, start):
		sentence = [start]

		while sentence[-1] is not End:
			most_common = words[sentence[-1]].most_common()
			random.shuffle(most_common)

			if len(most_common) < 2:
				break

			for word, _ in most_common:
				if word is End and len(sentence) < 20:
					continue
				else:
					sentence.append(word)
					break

		if sentence[-1] is End:
			sentence = sentence[:-1]
		if sentence[0] is Start:
			sentence = sentence[1:]

		return sentence

	@classmethod
	def generate(cls, filename, start = None):
		words_next = defaultdict(Counter)
		words_sentence = defaultdict(Counter)

		for line in open(filename):
			line = line.split()

			if len(line) < 2:
				continue

			for first, second in zip([Start] + line, line + [End]):
				words_next[first][second] += 1

				for word in line:
					words_sentence[first][word] += 1

		if not start:
			start = Start

		sentence = []

		i = 0
		while len(sentence) < 2:
			sentence = cls._generate4(words_next, start, words_sentence)
			i += 1

			if i > 1000:
				start = Start

		return " ".join(sentence)


class Hapotti(BotScript):
	def __init__(self, server_connection, config):
		BotScript.__init__(self, server_connection, config)

		self.material = config['material']

	def onChannelMessage(self, nick, target, message, full_mask):
		#if random.randint(0, 9) < 1:
		if self.server_connection.nick in message:
			words = message.split()[1:]
			print random.choice(words)

			self.say(target, nick + ", " + Bigram.generate(self.material, random.choice(words)))


if __name__ == '__main__':
	print Bigram.generate("/home/juke/git/bigrammi/hapo_tekstit.txt")