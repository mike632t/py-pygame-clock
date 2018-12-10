#!/usr/bin/python -s
#
# py-pygame-moon-clock.py
#
# This  program  is free software: you can redistribute it and/or  modify it
# under the terms of the GNU General Public License as published by the Free
# Software  Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This  program  is  distributed  in the hope that it will  be  useful,  but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public  License
# for more details.
#
# You  should  have received a copy of the GNU General Public License  along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# 14 Jan 18     0.A - Initial version - MEJT
# 17 Jan 18     0.B - Draws  the hands on a temporary surface which is  then
#                     rotated  this looks better as it keeps the ends of the
#                     hands square - MEJT
#                   - Moves the hour hand incrementally every minute - MEJT
#                   - Draws the border using two concentric circles to avoid
#                     the appearance of 'moire' patterns - MEJT
# 20 Jan 18         - Added  host IP address to display - MEJT
#  3 Feb 18         - Changed  object model to minimze the numbr of time the 
#                     background needs to be redrawn - MEJT
#  5 Feb 18         - Any wallpaper image is automatically tiled to fill the
#                     clock face - MEJT
# 26 Aug 18         - Added  an optional element to show if it is daytime or
#                     night time - MEJT
#
# To Do:            - Implement an hand object...
#
# Dependancies:     - python-pygame, python-tz
#
# https://www.codeday.top/2017/02/23/18371.html
# https://stackoverflow.com/questions/166506 - Get IP address

from datetime import datetime
from pytz import timezone
import pygame, numpy
import sys, math
import signal, socket
   
SMALL = 40
    
class clock(object):
  
  def __init__(self, _colour, _radius, _width = 0, _timezone = 'GMT', _title = None, _wallpaper = None):
    self.foreground = pygame.Color('light grey') # Minute hand
    self.background = pygame.Color('dark grey') # Hour hand
    self.highlight = pygame.Color('dark red') # Second hand
    self.colour = _colour
    self.radius = _radius
    self.width = _width
    self.timezone = _timezone
    self.title = _title
    self.size = self.width, self.height = (self.radius * 2, self.radius * 2)
    self.bitmap = pygame.Surface(self.size)
    
    font=pygame.font.Font(None,_radius //4) # Derive the font height from the radius
    image = font.render(' ', True, self.foreground)
    self.font_height = image.get_height()
    self.size = self.width, self.height
    self.bitmap = pygame.Surface(self.size, pygame.SRCALPHA)
    
    # Fill in the background
    if _wallpaper is not None:
      _picture = pygame.image.load(_wallpaper).convert_alpha()
      _tile(self.bitmap, _picture)
    else:
      pygame.draw.circle(self.bitmap, _colour, (self.radius, self.radius) , self.radius - _width)
    
    # Draw the dial
    _buffer = pygame.Surface(self.size, pygame.SRCALPHA)
    pygame.draw.circle(_buffer, self.foreground, (self.radius, self.radius) , self.radius)
    pygame.draw.circle(_buffer, (0, 0, 0, 0), (self.radius, self.radius) , self.radius - _width)
    #self.bitmap.blit(_buffer, (0, 0), None, pygame.BLEND_RGBA_MULT)
    self.bitmap.blit(_buffer, (0, 0))
    del _buffer
    
    # Draw the numbers on the dial.
    if _radius >= SMALL:
      for n in range(1,13):
        image = font.render(str(n), True, self.foreground)
        _angle = math.radians(n * (360 / 12) - 90)
        x = math.cos(_angle) * (self.radius - self.font_height) - self.font_height // 2 # Calculate the where to put the number allowing for it's size
        y = math.sin(_angle) * (self.radius - self.font_height) - self.font_height // 2
        self.bitmap.blit(image, (self.radius + int(x), _radius + int(y))) # Draw the number on the bitmap
  
      if self.title is not None:    
        _image = font.render(str(_title + ' '), True, self.foreground)
        self.bitmap.blit(_image, (self.radius - _image.get_width() // 2, _radius * .75 - _image.get_height() // 2)) # Draw the title
    
    # Create a mask
    _mask = pygame.Surface(self.size, pygame.SRCALPHA)
    pygame.draw.circle(_mask, (pygame.Color('white')), (self.radius, self.radius) , self.radius)
    self.bitmap.blit(_mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
    
    
  def draw(self, _surface, _position):
    
    # get the time of day
    _now = timezone(self.timezone).normalize(datetime.now(timezone('UTC')))
    _hours = _now.hour
    _minutes = _now.minute
    _seconds = _now.second
    
    _buffer = pygame.Surface.copy(self.bitmap)
    
    if self.radius < SMALL or self.highlight is None:
      # Draw the day/night wheel 
      _length = int(self.radius * .9 - 2 * self.font_height + .5) * 2
      _image = pygame.Surface((_length, _length), pygame.SRCALPHA) # Create a drawing surface for the wheel
      channels = []
      for channel in range(3):
        _source, _dest = pygame.Color('midnightblue')[channel], pygame.Color('skyblue')[channel]
        channels.append(numpy.tile(numpy.linspace(_source, _dest, _length), [_length, 1],),)
      _gradient = numpy.dstack(channels)
      pygame.surfarray.blit_array(_image, pygame.surfarray.map_array(_image, _gradient),)
      
      _mask = pygame.Surface((_length, _length), pygame.SRCALPHA)
      pygame.draw.circle(_mask, (pygame.Color('white')), (_length  // 2, _length // 2) , _length //2)  
      _image.blit(_mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
      
      _width = _length // 5
      _moon = pygame.Surface((_width, _width), pygame.SRCALPHA)
      _moon.fill((179, 179, 179)) # Fill shape with foreground colour
      _mask = pygame.Surface((_width, _width), pygame.SRCALPHA) # Create a mask
      pygame.draw.circle(_mask, (pygame.Color('white')), (_width // 2, _width // 2) , _width // 2)
      pygame.draw.circle(_mask, (0, 0, 0, 0),            (_width // 2 - _width // 4, _width // 2 + _width // 5), int( _width / 2.25)) # Mask off some of the moon to make a cresent shape
      _moon.blit(_mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
      #_moon = pygame.transform.rotate(_moon, -30)  
      _image.blit(_moon, ((_length - _moon.get_width()) // 2, (_width - _moon.get_height()) // 2 + _length // 32))
        
      _width = _length // 5
      #_sun = pygame.Surface((_width, _width), pygame.SRCALPHA)
      #_sun.fill((250, 214, 75)) # Fill shape with foreground colour
      #_mask = pygame.Surface((_width, _width), pygame.SRCALPHA) # Create a mask
      #pygame.draw.circle(_mask, (pygame.Color('white')), (_width // 2, _width // 2) , _width // 2)
      #_sun.blit(_mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
      #_image.blit(_sun, ((_length - _sun.get_width()) // 2, (_length - _sun.get_height()) - _length // 32))
      pygame.draw.circle(_image, (250, 214, 75), ((_length - _width) // 2, (_length - _width // 2 - _length // 16)) , _width // 2)
        
      pygame.draw.circle(_image, (0, 0, 0, 0), (_length // 2, _length // 2 ), (_length) // 2 - _width - _length // 16) # Make the middle of the wheel transparent.
        
      _image = pygame.transform.rotate(_image, abs(((12 - _hours + float(_minutes) / 60) * 15)%360))
      
      pygame.draw.polygon(_image, (0, 0, 0, 0), ((0, 0), 
                                              (0, _image.get_height() // 2 + _length // 8), 
                                              (_image.get_width() // 2 , _image.get_height() // 2), 
                                              (_image.get_width(), _image.get_height() // 2 + _length // 8), 
                                              (_image.get_width(), 0))) # Mask out hidden part of the dial.
      
      _buffer.blit(_image, ((_buffer.get_width() - _image.get_width() + .5) // 2, (_buffer.get_height() - _image.get_height() + .5) // 2))
      del _image

    # Draw the hour hand
    _angle = abs(((_hours + float(_minutes) / 60) * 30)%360)
    _length = self.radius * .9 - 2 * self.font_height
    _width = self.radius // 16 + 1
    _image = pygame.Surface(self.size, pygame.SRCALPHA) # Create a drawing surface for the hour hand
    pygame.draw.line(_image, self.background, (self.radius, self.radius), (self.radius, self.radius - _length - 1), _width)
    _image = pygame.transform.rotate(_image,-_angle)
    _buffer.blit(_image, ((_buffer.get_width() - _image.get_width()) // 2, (_buffer.get_height() - _image.get_height()) // 2))
    del _image    
    
    # Draw the minute hand
    _angle = abs(((_minutes + (_seconds // 30 / 2.0)) * 6) % 360)
    _length = self.radius - 2 * self.font_height
    _width = self.radius //24 +1
    _image = pygame.Surface(self.size, pygame.SRCALPHA) # Create a drawing surface for the minute hand
    pygame.draw.line(_image, self.foreground, (self.radius, self.radius), (self.radius, self.radius - _length - 1), _width)
    _image = pygame.transform.rotate(_image,-_angle)
    _buffer.blit(_image, ((_buffer.get_width() - _image.get_width()) // 2, (_buffer.get_height() - _image.get_height()) // 2))
    pygame.draw.circle(_buffer, self.foreground, (self.radius, self.radius) ,  self.radius // 20 + 1)
    del _image 
    
    # Draw the second hand
    if self.radius >= SMALL and self.highlight is not None:
      _angle = abs((_seconds * 6) % 360)
      _length = self.radius * 1.05 - 2 * self.font_height
      _width = self.radius // 32 + 1
      _image = pygame.Surface(self.size, pygame.SRCALPHA) # Create a drawing surface for the minute hand
      pygame.draw.line(_image, self.highlight, (self.radius, self.radius), (self.radius, self.radius - _length - 1), _width)
      _image = pygame.transform.rotate(_image,-_angle)
      _buffer.blit(_image, ((_buffer.get_width() - _image.get_width()) // 2, (_buffer.get_height() - _image.get_height()) // 2))
      pygame.draw.circle(_buffer, self.highlight, (self.radius, self.radius) ,  self.radius // 20 + 1)
      del _image 
    
    _surface.blit(_buffer, (_position[0] - self.size[0] // 2, _position[1] - self.size[1] // 2))
    del _buffer
  
    
def _tile(_bitmap,_wallpaper):
  for x_offset in range(0,_bitmap.get_width(),_wallpaper.get_width()):
    for y_offset in range(0,_bitmap.get_height(),_wallpaper.get_height()):
      _bitmap.blit(_wallpaper,(x_offset,y_offset)) 
  
  
def _scan():
  event = pygame.event.poll()
  if event.type == pygame.QUIT:
    pygame.quit()
    sys.exit()
  elif event.type == pygame.KEYDOWN:
    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
      return False
  return True
 
 
def _abort(signal, frame):
  pygame.quit()
  exit(0) 
 
 
def _handler(signum, frame):
  pass
 
 
FPS = 60
_size = WIDTH, HEIGHT = (800 , 480)

signal.signal(signal.SIGHUP, _handler)
signal.signal(signal.SIGINT, _abort) # Set up interrupt event handlers.
signal.signal(signal.SIGTERM, _abort)


try:
  pygame.init()
except AttributeError:
  pass

pygame.font.init()
pygame.mouse.set_visible(False)
pygame.display.set_caption("Clock")
screen = pygame.display.set_mode((_size))
screen.fill(pygame.Color('black'))

try:
  connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  connection.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  connection.connect(('<broadcast>', 0))
  address = connection.getsockname()[0]
except IOError:
  address = ''


icon = pygame.Surface((128, 138)) # Create a drawing surface for the icon
icon.fill(pygame.Color('black'))
icon.set_colorkey(pygame.Color('black'))
_clock = clock(pygame.Color('dim grey'), 64, 1)
_clock.draw(icon, (64, 64))
pygame.display.set_icon(icon) # Set it as the windows icon!

font=pygame.font.Font(None, 16) # Derive the font height from the radius
text = font.render(address, True, pygame.Color('dark gray'))

_background = pygame.Surface((_size)) # Create a drawing surface for the background
_background.fill(pygame.Color('grey5'))

_wallpaper = pygame.image.load("tile.png")
#_tile(_background, _wallpaper)
_background.blit(text, (2, screen.get_height() - text.get_height()))

_Auckland = clock(pygame.Color('dim grey'), 64, 2, 'Pacific/Auckland', 'Auckland')
_Auckland.highlight = None

_Hong_Kong = clock(pygame.Color('dim grey'), 64, 2, 'Asia/Hong_Kong', 'Hong Kong')
_Hong_Kong.highlight = None

_Perth = clock(pygame.Color('dim grey'), 64, 2, 'Australia/Perth', 'Perth')
_Perth.highlight = None

_Paris = clock(pygame.Color('dim grey'), 64, 2, 'Europe/Paris', 'Paris')
_Paris.highlight = None

_New_York = clock(pygame.Color('dim grey'), 64, 2, 'America/New_York', 'New York')
_New_York.highlight = None

_London = clock(pygame.Color('dim grey'), 160, 6, 'Europe/London', '', 'background.png')

screen.blit(_background, (0, 0))
while _scan():
  _New_York.draw(screen, (100, 72))
  _Paris.draw(screen, (250, 72))
  _Perth.draw(screen, (400, 72))
  _Hong_Kong.draw(screen, (550, 72))
  _Auckland.draw(screen, (700, 72))
  _London.draw(screen, (400, 312 ))
  pygame.display.flip()
  pygame.time.Clock().tick(FPS)

del _clock
 
pygame.quit()
exit(0)
