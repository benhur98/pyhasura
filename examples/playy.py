import vlc

class Song(object):
    def __init__(self,url):
        self.url=url
    def initalize(self):
        self.p=vlc.MediaPlayer(self.url)
    def play(self):
        self.p.play()
    def stop(self):
        self.p.stop()
