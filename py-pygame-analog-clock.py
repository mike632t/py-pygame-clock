#!/usr/bin/python -s
#
# py-pygame-analog-clock.py
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
#  3 Feb 18         - Changed object model to minimise the numbr of time the 
#                     background needs to be redrawn - MEJT
#  5 Feb 18         - Any wallpaper oe background image is tiled to fill the
#                     available space - MEJT
# 12 Dec 18         - Displays  the windows background and clock face  using 
#                     the specified colour if the bitmaps are missing - MEJT
#                   - Colours now defined as constants - MEJT
#                   - Added a function to allow the a null string to be used 
#                     as  a valid colour name indicate that an object should
#                     be transparent - MEJT
#                   - Fixed  transparency issue (by redrawing the background
#                     every time the display is updated) - MEJT
#                   - Grouped  all the code that is part of the clock  class 
#                     together  and made the execution of the  demonstration
#                     routine conditional - MEJT
#                   - Added  a new text property to allow the colour of  the
#                     digits  to be defined separately from the minute  hand
#                     if desired - MEJT
#
# To Do:            - Implement an hand object...
#
# Dependencies:     - python-pygame, python-tz
#
# https://www.codeday.top/2017/02/23/18371.html
# https://stackoverflow.com/questions/166506 - Get IP address


class Clock(object):
  
  def __init__(self, _colour, _radius, _width = 0, _timezone = 'GMT', _title = None, _wallpaper = None):
  
    import pygame
    import numpy
    import math
    
    self.background = pygame.Color('grey') # Hour hand
    self.foreground = pygame.Color('light grey') # Minute hand
    self.highlight = pygame.Color('red') # Second hand
    self.text = self.foreground
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
    
    try: # Fill in the background - try loading an image and fill it with a colour if it fails to load
      _picture = pygame.image.load(_wallpaper).convert_alpha()
      _tile(self.bitmap, _picture)
    except Exception as _error:
      pygame.draw.circle(self.bitmap, self.colour, (self.radius, self.radius) , self.radius - _width)
    
    # Draw the dial
    _buffer = pygame.Surface(self.size, pygame.SRCALPHA)
    pygame.draw.circle(_buffer, self.foreground, (self.radius, self.radius) , self.radius)
    pygame.draw.circle(_buffer, (0, 0, 0, 0), (self.radius, self.radius) , self.radius - _width)
    self.bitmap.blit(_buffer, (0, 0))
    del _buffer
    
    # Draw the numbers on the dial
    if _radius >= 40: # Don't draw numbers if the radius is less than 40 pixels - there isn't enough space
      for n in range(1,13):
        image = font.render(str(n), True, self.text)
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

    import pygame
    from datetime import datetime
    from pytz import timezone
    
    # Get the time of day (GMT)
    _now = timezone(self.timezone).normalize(datetime.now(timezone('UTC')))
    _hours = _now.hour
    _minutes = _now.minute
    _seconds = _now.second
    
    _buffer = pygame.Surface.copy(self.bitmap)
    
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
    _angle = abs(((_minutes + (_seconds // 30 / 2.0)) * 6) % 360) # Updates twice a minute
    _length = self.radius - 2 * self.font_height
    _width = self.radius //24 +1
    _image = pygame.Surface(self.size, pygame.SRCALPHA) # Create a drawing surface for the minute hand
    pygame.draw.line(_image, self.foreground, (self.radius, self.radius), (self.radius, self.radius - _length - 1), _width)
    _image = pygame.transform.rotate(_image,-_angle)
    _buffer.blit(_image, ((_buffer.get_width() - _image.get_width()) // 2, (_buffer.get_height() - _image.get_height()) // 2))
    pygame.draw.circle(_buffer, self.foreground, (self.radius, self.radius) ,  self.radius // 20 + 1)
    del _image 
    
    # Draw the second hand
    if self.highlight is not None:
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
  

if __name__ == '__main__':

  WIDTH, HEIGHT = (800 , 480) # Size of window/display

  WALLPAPER = 'wallpaper.png' # Background wallpaper, clock will use background colour if bitmap does not exist
  IMAGE = 'background.png' # Background image for main clock face, clock will use selected clock face colour if bitmap does not exist
  BACKGROUND = 'black' # Background colour
  TEXT = 'white' # Text colour (used for IP address)

  LARGE_FACE = 'dark grey' # Colour of the large clock face (it will be transparent if no colour specified)
  LARGE_FACE = '' # Colour of the large clock face (it will be transparent if no colour specified)
  SMALL_FACE = 'dim grey' # Colour of the small clock faces (it will be transparent if no colour specified)

  FPS = 60
  import pygame
  import signal, socket
  
      
  def _tile(_bitmap,_wallpaper):
    for x_offset in range(0,_bitmap.get_width(),_wallpaper.get_width()):
      for y_offset in range(0,_bitmap.get_height(),_wallpaper.get_height()):
        _bitmap.blit(_wallpaper,(x_offset,y_offset)) 
    

  def _colour(_object):
    if _object is None or _object == '':
      return (0, 0, 0, 0)
    else:
      try:
        return pygame.Color(_object)
      except ValueError as _error:
        pass
         
    
  def _scan():
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
      pygame.quit()
      exit(0)
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
        return False
    return True
   
   
  def _abort(signal, frame):
    pygame.quit()
    exit(0) 
   
   
  def _handler(signum, frame):
    pass
    
   
  _size = WIDTH, HEIGHT

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
  screen.fill(_colour('black'))

  try:
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    connection.connect(('<broadcast>', 0))
    address = connection.getsockname()[0]
  except IOError:
    address = ''


  icon = pygame.Surface((128, 138)) # Create a drawing surface for the icon
  icon.fill(_colour('black'))
  icon.set_colorkey(_colour('black'))
  _clock = Clock(_colour('dim grey'), 64, 1)
  _clock.draw(icon, (64, 64))
  pygame.display.set_icon(icon) # Set it as the windows icon!

  font=pygame.font.Font(None, 16) # Derive the font height from the radius
  text = font.render(address, True, _colour(TEXT))

  _background = pygame.Surface((_size)) # Create a drawing surface for the background

  try: # Fill in the wallpaper - try loading an image and fill the background with colour if it fails to load
    _wallpaper = pygame.image.load(WALLPAPER)
    _tile(_background, _wallpaper)
  except Exception as _error:
    _background.fill(_colour(BACKGROUND))

  _background.blit(text, (2, screen.get_height() - text.get_height()))

  _Auckland = Clock(_colour(SMALL_FACE), 64, 2, 'Pacific/Auckland', 'Auckland')
  _Auckland.highlight = None

  _Hong_Kong = Clock(_colour(SMALL_FACE), 64, 2, 'Asia/Hong_Kong', 'Hong Kong')
  _Hong_Kong.highlight = None

  _Perth = Clock(_colour(SMALL_FACE), 64, 2, 'Australia/Perth', 'Perth', '')
  _Perth.highlight = None

  _Paris = Clock(_colour(SMALL_FACE), 64, 2, 'Europe/Paris', 'Paris')
  _Paris.highlight = None

  _New_York = Clock(_colour(SMALL_FACE), 64, 2, 'America/New_York', 'New York')
  _New_York.highlight = None

  _London = Clock(_colour(LARGE_FACE), 160, 6, 'Europe/London', '', '')
  _London.text = _colour(TEXT)

  while _scan():
    screen.blit(_background, (0, 0)) # Redrawing the background every time the display is updated fixes the transparency issue 
    _New_York.draw(screen, (100, 72))
    _Paris.draw(screen, (250, 72))
    _Perth.draw(screen, (400, 72))
    _Hong_Kong.draw(screen, (550, 72))
    _Auckland.draw(screen, (700, 72))
    _London.draw(screen, (400, 312 ))
    pygame.display.flip()
    pygame.time.Clock().tick(FPS)

  pygame.quit()
  exit(0)
