#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file dafgen.py
@author Sam Freeside <snovvcrash@protonmail[.]ch>
@date 2018-01

@brief Simple DAF (Delayed Auditory Feedback) Generator

@license
Copyright (C) 2018 Sam Freeside

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endlicense
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from ui_dafgen import Ui_DAFGen

from pyaudio import PyAudio, paFloat32
from math import floor, ceil
from time import perf_counter

import sys


class Worker(QThread):
	"""Worker thread that reads and writes audio samples between a ring buffer and the audio hardware.
		If the ring buffer conatins audio data at index _ring[_pring], it is written out for playback.
		Next, the current recorded chunk of audio frames is read into _ring[_pring] and _pring is advanced,
		creating a delay since the sample isn't played until the next time around the ring buffer
	"""

	# use to propagate the timing info back to the ui
	_trigger = Signal(float)
	# ring buffer for the frame chunks
	_ring:list = []
	# current position in the ring
	_pring:int = 0
	# timestamp of the last time the ring size was changed
	_rscBuffer:float = 0.0

	def __init__(self, bufferSize:int, ringSize:int, streamIn:PyAudio.Stream, streamOut:PyAudio.Stream, ringSizeSignal:Signal) -> None:
		"""Initialize internal state of the Worker

		Args:
			bufferSize: number of audio frames to put in each chunk
			ringSize: number of slots in the ring buffer
			streamIn: pyaudio input stream
			streamOut: pyaudio output stream
			ringSizeSignal: 		
		"""

		QThread.__init__(self)
		self._bufferSize:int = bufferSize
		self._streamIn:int = streamIn
		self._streamOut:int = streamOut
		# do an initial resize so ring isn't length zero
		self._resizeRing(ringSize)
		# connect the UI signal to ringSizeChanged() slot
		ringSizeSignal.connect(self.ringSizeChanged)

	def __del__(self):
		self.wait()

	def ringSizeChanged(self, ringSize:int) -> None:
		"""QSlot that recieves ring size change messages from the UI

		Args:
			ringSize: number of slots in the ring buffer
		"""

		# limit to changing ring size once per hundredth of a second
		ts = perf_counter()
		# if "old" timestamp isn't at least 0.01 seconds in the past
		if self._rscBuffer > ts - 0.01:
			return # bail
		
		# actually do the resize
		self._resizeRing(ringSize)
		# update the resize timestamp
		self._rscBuffer = ts

	def _resizeRing(self, ringSize:int) -> None:
		"""Resizes _ring to contain ringSize elements by adding to or removing the elements directly after _pring,
		    also adjusting it if necessary

		Args:
			ringSize: number of slots in the ring buffer
		"""

		# calculate the difference between the requested ringSize and the current length of _ring
		sizeDiff:int = ringSize - len(self._ring)
		# sizeDiff is positive, just add empty spaces to the ring buffer
		if sizeDiff > 0:
			# fancy python list slicing makes this ez
			self._ring = self._ring[:self._pring] + ([ None ] * sizeDiff) + self._ring[self._pring + 1:]
		# sizeDiff is negative, this means removing elements
		if sizeDiff < 0:
			# make sizeDiff positive to simplify things
			sizeDiff = -sizeDiff
			# calculate the number of element remaining in _ring after _pring's position
			spaceAfter:int = len(self._ring) - self._pring
			if spaceAfter > sizeDiff:
				# there is enough space after _pring, just remove the slots and be done
				skipAfter = self._pring + sizeDiff
				# slice and done
				self._ring = self._ring[:self._pring] + self._ring[skipAfter:]
			else:
				# there are not enough slots in _ring after _pring to remove the requested number of elements
				# assume removal of all elements after _pring and calculate how many more need
				# to be removed from the very beginning of _ring
				skipBefore = sizeDiff - spaceAfter
				# slice
				self._ring = self._ring[skipBefore:self._pring]
				# due to elements being removed at the beginning of _ring, move _pring back too
				self._decPRing(skipBefore)

	def _genDAF(self) -> None:
		"""Loops forever reading and writing frames"""

		# initialize the performance varible
		start:int = 0
		# loop forever until the input stream dies
		while self._streamIn.is_active():
			# only set the perf var when _pring is zero
			if not start and self._pring == 0:
				start = perf_counter()
			# only write _ring audio frame chunks to the output stream if they exist
			if self._ring[self._pring] != None:
				self._streamOut.write(self._ring[self._pring])
			# read a new set of audio frames into the current spot in _ring
			self._ring[self._pring] = self._streamIn.read(self._bufferSize)
			# increment _pring
			self._incPRing(1)
			# check if there is a perf var stored and _pring in on zero
			if start and self._pring == 0:
				# calculate and emit performance statistics for the UI
				actualDelay = perf_counter() - start
				self._trigger.emit(actualDelay)
				# reset the timing loop
				start = 0

	def _incPRing(self, num:int) -> None:
		"""Increases _pring by num modulo the current size of _ring"""
		self._pring = (self._pring + num) % len(self._ring)

	def _decPRing(self, num:int) -> None:
		"""Decreases _pring by num modulo the current size of _ring"""
		self._incPRing(-num)

	def run(self):
		self._genDAF()


class MainApp(QMainWindow, Ui_DAFGen):

	_ringSizeSignal = Signal(int)

	_CHANNELS = 2
	_RATE = 44100
	_BUFFERSIZE = 100
	_BUFFERSPERSECOND = _RATE / _BUFFERSIZE

	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.stopButton.setEnabled(False)
		self._updateDelay()

		self.delaySlider.valueChanged.connect(self._updateDelay)
		self.startButton.clicked.connect(self._startCapture)
		self.stopButton.clicked.connect(self._stopCapture)
		self.quitButton.clicked.connect(self._quit)

	def _quit(self):
		self._stopCapture()
		QApplication.quit()

	def _updateDelay(self):
		v = self.delaySlider.value()
		self.delayEdit.setPlainText(f"{v} ms")
		if 50 >= v >= 200:
			return
		ringSize = self._calcRingSize(v)
		self._ringSizeSignal.emit(ringSize)

	def _startCapture(self):
		ringSize = self._calcRingSize(self.delaySlider.value())
		device = PyAudio()

		try:
			streamIn = device.open(
				format=paFloat32,
				channels=self._CHANNELS,
				rate=self._RATE,
				input=True,
				frames_per_buffer=self._BUFFERSIZE
			)

			streamOut = device.open(
				format=paFloat32,
				channels=self._CHANNELS,
				rate=self._RATE,
				output=True,
				frames_per_buffer=self._BUFFERSIZE
			)

		except OSError as e:
			QMessageBox.critical(self, 'Error', 'No input/output device found! Connect and rerun.')
			return

		self._workerThread = Worker(self._BUFFERSIZE, ringSize, streamIn, streamOut, self._ringSizeSignal)
		self._workerThread._trigger.connect(self._updateActualDelay)

		self.startButton.setEnabled(False)
		self.stopButton.setEnabled(True)

		self._workerThread.start()

	def _calcRingSize(self, ms: int) -> int:
		return floor(round(ms / 1000 * self._BUFFERSPERSECOND))

	def _stopCapture(self):
		if self._workerThread:
			self._workerThread.terminate()

		self.actualDelayEdit.clear()
		self.startButton.setEnabled(True)
		self.stopButton.setEnabled(False)

	def _updateActualDelay(self, t):
		newValue = floor(t * 1000)
		self.actualDelayEdit.setPlainText(str(newValue) + ' ms')

	def closeEvent(self, event:QEvent):
		self._quit()

def main():
	app = QApplication(sys.argv)
	win = MainApp()
	win.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()
