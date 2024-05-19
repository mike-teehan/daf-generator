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

	_trigger = Signal(float)
	_ring:list = []
	_pring:int = 0
	_rscBuffer:float = 0.0

	def __init__(self, bufferSize:int, ringSize:int, streamIn:PyAudio.Stream, streamOut:PyAudio.Stream, ringSizeSignal:Signal) -> None:
		QThread.__init__(self)
		self._bufferSize:int = bufferSize
		self._streamIn:int = streamIn
		self._streamOut:int = streamOut
		self._resizeRing(ringSize)
		ringSizeSignal.connect(self.ringSizeChanged)

	def __del__(self):
		self.wait()

	def ringSizeChanged(self, ringSize:int) -> None:
		ts = perf_counter()
		if self._rscBuffer > ts - 0.01:
			return
		self._resizeRing(ringSize)
		self._rscBuffer = ts

	def _resizeRing(self, ringSize:int) -> None:
		sizeDiff:int = ringSize - len(self._ring)
		if sizeDiff > 0:
			self._ring = self._ring[:self._pring] + ([ None ] * sizeDiff) + self._ring[self._pring + 1:]
		if sizeDiff < 0:
			spaceAfter:int = len(self._ring) - self._pring
			if spaceAfter > -sizeDiff:
				self._ring = self._ring[:self._pring] + self._ring[self._pring + sizeDiff:]
			else:
				skipBefore = -sizeDiff - spaceAfter
				self._ring = self._ring[skipBefore:self._pring]
				self._decPRing(skipBefore + 1)

	def _genDAF(self) -> None:
		start:int = 0
		while self._streamIn.is_active():
			if not start and self._pring == 0:
				start = perf_counter()
			if self._ring[self._pring] != None:
				self._streamOut.write(self._ring[self._pring])
			self._ring[self._pring] = self._streamIn.read(self._bufferSize)
			self._incPRing(1)
			if start and self._pring == 0:
				actualDelay = perf_counter() - start
				self._trigger.emit(actualDelay)
				start = 0

	def _incPRing(self, num:int) -> None:
		self._pring = (self._pring + num) % len(self._ring)

	def _decPRing(self, num:int) -> None:
		self._pring = (self._pring - num) % len(self._ring)

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
