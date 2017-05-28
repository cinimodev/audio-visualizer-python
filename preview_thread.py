from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt
import core
import time
from queue import Queue, Empty
import numpy

class Worker(QtCore.QObject):

  imageCreated = pyqtSignal(['QImage'])

  def __init__(self, parent=None, queue=None):
    QtCore.QObject.__init__(self)
    parent.newTask.connect(self.createPreviewImage)
    parent.processTask.connect(self.process)
    self.core = core.Core()
    self.queue = queue
    self.core.settings = parent.settings
    self.stackedWidget = parent.window.stackedWidget


  @pyqtSlot(str, list)
  def createPreviewImage(self, backgroundImage, components):
    # print('worker thread id: {}'.format(QtCore.QThread.currentThreadId()))
    dic = {
      "backgroundImage": backgroundImage,
      "components": components,
    }
    print(components)
    self.queue.put(dic)

  @pyqtSlot()
  def process(self):
    try:
      nextPreviewInformation = self.queue.get(block=False)
      while self.queue.qsize() >= 2:
        try:
          self.queue.get(block=False)
        except Empty:
          continue

      bgImage = self.core.parseBaseImage(\
                   nextPreviewInformation["backgroundImage"],
                   preview=True
                )
      if bgImage == []:
        bgImage = ''
      else:
        bgImage = bgImage[0]

      im = self.core.drawBaseImage(bgImage)
      frame = Image.new("RGBA", (1280, 720),(0,0,0,255))
      frame.paste(im)


      componentWidgets = [self.stackedWidget.widget(i) for i in range(self.stackedWidget.count())]
      components = nextPreviewInformation["components"]
      print(components)
      print(componentWidgets)
      for component, componentWidget in zip(components, componentWidgets):
        print('drawing')
        newFrame = Image.alpha_composite(frame,component.previewRender(self, componentWidget))
        frame = Image.alpha_composite(frame,newFrame)

      self._image = ImageQt(frame)
      self.imageCreated.emit(QtGui.QImage(self._image))
      
    except Empty:
      True
