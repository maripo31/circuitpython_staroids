
# staroids_code.py -- fakey Almost Asteroids
# 4 Aug 2021 - @todbot
import board, time, math, random
import displayio, terminalio, bitmaptools
import adafruit_imageload
from adafruit_display_text import bitmap_label as label
import os

num_ship_tiles = 36
num_roid_tiles = 120

board_type = os.uname().machine

# Macropad 128x64 monochrome display, uses 4/5/6 keys for L/T/R
if 'Macropad' in board_type:
    import keypad
    import neopixel
    num_roids = 3
    num_shots = 3
    shot_life = 0.4
    accel_max_shot = 4
    accel_max_ship = 0.08
    vmax = 3
    tile_w = 12
    tile_h = 12
    ship_fname = '/imgs/ship_12_sheet.bmp'
    roid_fnames = ['/imgs/roid0_12_sheet.bmp', '/imgs/roid1_12_sheet.bmp']
    roidexp_fname = '/imgs/roidexp_12_sheet.bmp'
    shot_fname = '/imgs/shotsm3.bmp' # shot fname has smaller tile
    bg_fname = '/imgs/bg_stars_mono.bmp'
    leds = neopixel.NeoPixel(board.NEOPIXEL, 12, brightness=0.1)
    # stolen from adafruit_macropad, thx kattni!
    keypins = [getattr(board, "KEY%d" % (num + 1)) for num in (list(range(12)))]
    keys = keypad.Keys(keypins, value_when_pressed=False, pull=True)
    # Macropad, key processing
    def get_user_input(turning,thrusting):
        key = keys.events.get()
        if key:
            if key.key_number == 3:  # KEY4 rotate LEFT
                turning = -0.15 if key.pressed else 0
            if key.key_number == 5:  # KEY6 rotate RIGHT
                turning = 0.15 if key.pressed else 0
            if key.key_number == 4:  # KEY5 THRUST/FIRE!
                thrusting = key.pressed
        return turning, thrusting
# FunHouse 240x240 color display, only 3 buttons so L/T/F (when rotated 90-deg)
elif 'FunHouse' in board_type:
    import digitalio
    import adafruit_dotstar
    num_roids = 4
    num_shots = 4
    shot_life = 1
    accel_max_shot = 4
    accel_max_ship = 0.2
    vmax = 5
    tile_w = 30
    tile_h = 30
    ship_fname = '/imgs/ship_30_sheet.bmp'
    roid_fnames = ['/imgs/roid0_30_sheet.bmp', '/imgs/roid1_30_sheet.bmp']
    roidexp_fname = '/imgs/roidexp_30_sheet.bmp'
    shot_fname = '/imgs/shotsm3.bmp' # shot fname has smaller tile
    bg_fname = '/imgs/bg_starfield.bmp' # hubble star field for funhouse
    button_L = digitalio.DigitalInOut(board.BUTTON_UP)     # turn left
    button_L.switch_to_input(pull=digitalio.Pull.DOWN)
    button_R = digitalio.DigitalInOut(board.BUTTON_DOWN)   # turn right
    button_R.switch_to_input(pull=digitalio.Pull.DOWN)
    button_F = digitalio.DigitalInOut(board.BUTTON_SELECT) # thrust!
    button_F.switch_to_input(pull=digitalio.Pull.DOWN)
    leds = adafruit_dotstar.DotStar(board.DOTSTAR_CLOCK,board.DOTSTAR_DATA,5,brightness=0.1)
    # Funhouse, key processing
    def get_user_input(turning,thrusting):
        thrusting = button_F.value
        turning = 0
        # check on the user
        if button_L.value:  # rotate LEFT
            turning = -0.15
        if button_R.value:  # rotate RIGHT
            turning = 0.15
        if button_F.value:  # THRUST/FIRE!
            thrusting = True
        return turning, thrusting
    
# Pybadge 160x128 color display, D-pad L/R for L/R, A for Thrust/Fire
elif 'Pybadge' in board_type:
    import keypad
    import neopixel
    num_roids = 3
    num_shots = 3
    shot_life = 0.5
    accel_max_shot = 3
    accel_max_ship = 0.06
    vmax = 3
    tile_w = 20
    tile_h = 20
    ship_fname = '/imgs/ship_20_sheet.bmp'
    roid_fnames = ['/imgs/roid0_20_sheet.bmp', '/imgs/roid1_20_sheet.bmp']
    roidexp_fname = '/imgs/roidexp_20_sheet.bmp'
    shot_fname = '/imgs/shotsm3.bmp' # shot fname has smaller tile
    bg_fname = '/imgs/bg_starfield.bmp' # hubble star field for funhouse
    keys = keypad.ShiftRegisterKeys(clock=board.BUTTON_CLOCK,data=board.BUTTON_OUT,
                                    latch=board.BUTTON_LATCH, key_count=8,
                                    value_when_pressed=True)
    leds = neopixel.NeoPixel(board.NEOPIXEL, 5, brightness=0.1)
    # Pybadge, key processing
    def get_user_input(turning,thrusting):
        key = keys.events.get()
        if key:
            if key.key_number == 7:  # KEY4 rotate LEFT
                turning = -0.12 if key.pressed else 0
            if key.key_number == 4:  # KEY6 rotate RIGHT
                turning = 0.12 if key.pressed else 0
            if key.key_number == 1:  # KEY5 THRUST/FIRE!
                thrusting = key.pressed
        return turning, thrusting

# Clue 240x240 color display, A/B for L/R, touch pad 2 (D2) for Thrust/Fire
elif 'clue' in board_type.lower():
    import keypad
    import neopixel
    import touchio
    num_roids = 3
    num_shots = 3
    shot_life = 0.5
    accel_max_shot = 3
    accel_max_ship = 0.06
    vmax = 3
    tile_w = 20
    tile_h = 20
    ship_fname = '/imgs/ship_20_sheet.bmp'
    roid_fnames = ['/imgs/roid0_20_sheet.bmp', '/imgs/roid1_20_sheet.bmp']
    roidexp_fname = '/imgs/roidexp_20_sheet.bmp'
    shot_fname = '/imgs/shotsm3.bmp' # shot fname has smaller tile
    bg_fname = '/imgs/bg_starfield.bmp' # hubble star field
    shooty = touchio.TouchIn(board.D2)
    keys = keypad.Keys([board.BUTTON_A, board.BUTTON_B], value_when_pressed=False, pull=True)
    leds = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
    # Clue, key processing
    def get_user_input(turning,thrusting):
        key = keys.events.get()
        if key:
            if key.key_number == 0:  # A rotate LEFT
                turning = -0.15 if key.pressed else 0
            if key.key_number == 1:  # B rotate RIGHT
                turning = 0.15 if key.pressed else 0
        thrusting = shooty.value
        return turning, thrusting
    
else:
    raise OSError("unknown board")

# helper object for physics things
class Thing:
    def __init__(self, x,y, w=0, vx=0,vy=0, angle=0, va=0, tilegrid=None, num_tiles=1):
        self.x, self.y, self.w = x, y, w  # x,y pos and width
        self.vx,self.vy = vx,vy # initial x,y velocity
        self.angle = angle # angle object is rotation
        self.va = va   # initial angular velocity
        self.vmax = vmax  # max velocity. 3 on pybadge, 4 on FunHouse 
        self.tg = tilegrid
        self.num_tiles = num_tiles
        self.time = 0
    def accelerate(self,angle, amount):
        self.vx = max(min(self.vx + (math.sin(angle) * amount), self.vmax),-self.vmax)
        self.vy = max(min(self.vy - (math.cos(angle) * amount), self.vmax),-self.vmax)
    def update_pos(self, alt_sprite_index=0):
        self.x = (self.x + self.vx) % display.width  # wrap around top-bottom
        self.y = (self.y + self.vy) % display.height # and left-right
        self.tg.x = int(self.x) - self.w//2 # we think in zero-centered things
        self.tg.y = int(self.y) - self.w//2 # but tilegrids are top-left zero'd
        #self.angle = (self.angle + self.va) % (math.pi*2)  # if object is spinning & constrain
        self.angle += self.va   # if object is spinning
        # get a tilegrid index based on angle and number of tiles total
        i = round(math.degrees(self.angle) / (360 / self.num_tiles)) % self.num_tiles
        self.tg[0] = i + (alt_sprite_index * self.num_tiles)
    def set_pos(self,obj):
        self.x, self.y = obj.x, obj.y
        self.vx, self.vy, self.va = obj.vx, obj.vy, obj.va
    def is_hit(self, obj):
        # try doing all as int math for speed
        if (int(self.x) > int(obj.x)-hitbox and int(self.x) < int(obj.x)+hitbox and
            int(self.y) > int(obj.y)-hitbox and int(self.y) < int(obj.y)+hitbox):
                return True
        return False
    def hide(self,hide=True):
        self.tg.hidden=hide
    @property
    def hidden(self):
        return self.tg.hidden
    # ship angle seems wrong for shots at times (floating point errors? or me?),
    # so this computes a new angle based off the very coarse tile grid rotation
    # I *think* it fixes the weird "off-axis" shots I was seeing 
    @property
    def angle_from_tile_index(self): 
        return self.tg[0] * (2*math.pi / self.num_tiles)

hitbox = tile_w//2

display = board.DISPLAY
display.auto_refresh=False
display.rotation = 0

screen = displayio.Group()  # group that holds everything
display.show(screen) # add main group to display

# ship sprites
ship_sprites,ship_sprites_pal = adafruit_imageload.load(ship_fname)
ship_sprites_pal.make_transparent(0)
shiptg = displayio.TileGrid(ship_sprites, pixel_shader=ship_sprites_pal,
                            width=1, height=1, tile_width=tile_w, tile_height=tile_h)
# asteroid sprites
roid_spr_pal = []
for f in roid_fnames: 
    spr,pal = adafruit_imageload.load(f)
    pal.make_transparent(0)
    roid_spr_pal.append( (spr,pal) )

# roid exploding sprite
roidexp_sprites, roidexp_sprites_pal = adafruit_imageload.load(roidexp_fname)
roidexp_sprites_pal.make_transparent(0)
roidexptg = displayio.TileGrid(roidexp_sprites, pixel_shader=roidexp_sprites_pal,
                               width=1, height=1, tile_width=tile_w, tile_height=tile_h)

# shot sprite
shot_sprites, shot_sprites_pal = adafruit_imageload.load(shot_fname)
shot_sprites_pal.make_transparent(0)

# get background image
bgimg, bgpal = adafruit_imageload.load(bg_fname)
screen.append(displayio.TileGrid(bgimg, pixel_shader=bgpal))

# create all the asteroids, add them to the screen
roids = []
for i in range(num_roids):
    vx,vy = random.uniform(-0.5,0.5), random.uniform(-0.2,0.2 ) # more x than y
    spr,pal = roid_spr_pal[ i % len(roid_spr_pal) ]
    roidtg = displayio.TileGrid(spr, pixel_shader=pal, width=1, height=1,
                                tile_width=tile_w, tile_height=tile_h)
    va = random.choice((-0.01,0.01)) # either rotate a little one way or other
    roid = Thing(display.width/2, display.height/2, w=tile_w, vx=vx, vy=vy, va=va,
                 tilegrid=roidtg, num_tiles=num_roid_tiles)
    roids.append(roid)
    screen.append(roid.tg)

# create shot objcts, add to screen, then hide them 
shots = []
for i in range(num_shots):
    shottg = displayio.TileGrid(shot_sprites, pixel_shader=shot_sprites_pal,
                                width=1, height=1, tile_width=3, tile_height=3)
    shot = Thing(display.width/2, display.height/2, tilegrid=shottg, num_tiles=1)
    shot.hide()
    shots.append(shot)
    screen.append(shottg)

# create ship object add it to the screen
ship = Thing( display.width/2, display.height/2, w=tile_w, vx=0.5, vy=0.2, angle=0, va=0,
              tilegrid=shiptg, num_tiles=num_ship_tiles)
screen.append(ship.tg)

# create explosion object, add to screen, but hide it
roidexp = Thing(display.width/2, display.height/2, w=tile_w, va=0.2,
                 tilegrid=roidexptg, num_tiles=8)
roidexp.hide() # initially don't show
screen.append(roidexp.tg)

# finally, add score display to screen
score_label = label.Label(font=terminalio.FONT, x=5, y=5, color=0x999999, text="000")
screen.append(score_label)

score = 0
point_roid = 1
point_ship = -3

# see if asteroid was hit and by what
def roid_hit(roid,hit_ship=False):
    global score
    print("hit")
    if hit_ship:
        leds.fill(0x9900ff)
        score = max(score + point_ship,0)
    else:
        leds.fill(0xff3300)
        score = max(score + point_roid,0)
    score_label.text = ("%03d" % score)
    roidexp.hide(False) # show explosion
    roidexp.set_pos(roid) # give it roid's position
    roidexp.va = 0.5  # gotta put back explosions spin
    roid.hide() # hide now exploded roid
    # and give it a new random location
    roid.x = random.randint(0,display.width)
    roid.y = random.randint(0,display.height)

# main loop
last_led_time = 0   # when was LED age last checked
last_roid_time = 0  # when was asteroid age last checked  
shot_time = 0       # when did shooting start
shot_index = -1     # which shot are we on
turning = 0 # neg if currrently turning left, pos if turning right
thrusting = False   # true if thrusting + firing
while True:
    now = time.monotonic()

    turning, thrusting = get_user_input(turning,thrusting)

    # update ship state
    ship.angle = ship.angle + turning
    if thrusting: 
        ship.accelerate( ship.angle, accel_max_ship) 
        if now - shot_time > 0.2:  # Fire ze missiles
            shot_time = now
            print("fire", ship.angle, ship.tg[0], ship.angle_from_tile_index)
            shot_index = (shot_index+1) % len(shots)
            shot = shots[shot_index]
            if shot.hidden:  # we can use this shot
                shot.x, shot.y = ship.x,ship.y # put shot at ship pos
                shot.vx,shot.vy = 0,0  # we accelerate it later
                shot.time = time.monotonic() # newborn!
                #shot.accelerate(ship.angle_from_tile_index, accel_max_shot) 
                shot.accelerate(ship.angle_from_tile_index, accel_max_shot) 
                shot.hide(False) # show it off

    # update ship position
    ship.update_pos( thrusting )
    
    # update asteroids state and positions
    for roid in roids:
        roid.update_pos()
        for shot in shots:
            if not shot.hidden and roid.is_hit(shot):
                roid_hit(roid) # FIXME magic value 0 and 1
                shot.hide()
        if roid.is_hit( ship ):
            roid_hit(roid,hit_ship=True)

    # update shot positions, age them out
    for shot in shots:
        shot.update_pos()
        if time.monotonic() - shot.time > shot_life: 
            shot.hide()
            
    # update position of our single explosion thing
    roidexp.update_pos()

    # age out the explosion, 1.5 = explosion lifetime
    if now - last_roid_time > 1.5:
        last_roid_time = now
        for roid in roids:
            if roid.hidden: # roid was shot
                roid.hide(False) # show it, its already in new location
        roidexp.hide() # don't need explosion any more

    display.refresh(target_frames_per_second=30)
    # time.sleep(0.0015)  # sets framerate

    #leds[0:] = [[max(i-10,0) for i in l] for l in leds] # dim all LEDs

    # LED aging and debug
    if time.monotonic() - last_led_time > 0.4:
        last_led_time = time.monotonic()
        leds.fill(0) # age out "you were hit" LEDs
        if 'Macropad' in board_type:
            leds[3:6] = (0x111111,0x111111,0x111111) # return them to on
        
        # roid = roids[0]
        # print("roid0: %d,%d vxy:%1.2f,%1.2f, a:%1.1f, %d" %
        #       (roid.x,roid.y, roid.vx,roid.vy, roid.angle, roid.tg[0]))
        # print("ship: %d,%d vxy:%1.2f,%1.2f, a:%1.1f, %d" %
        #       (ship.x,ship.y, ship.vx,ship.vy, ship.angle, ship.tg[0]))

