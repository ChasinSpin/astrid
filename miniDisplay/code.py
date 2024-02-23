import board
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from displayio import OnDiskBitmap, TileGrid, Group

main_group = Group()
img = OnDiskBitmap("images/logo.bmp")

tile_grid = TileGrid(bitmap=img, pixel_shader=img.pixel_shader)
main_group.append(tile_grid)

display = board.DISPLAY
display.root_group = main_group

tile_grid.x = 0
# display.width // 2 - width // 2

font = bitmap_font.load_font("fonts/Helvetica-Bold-16.bdf")

text_area = label.Label(font, text='SSID: myWifiNetwork', color=0x00FF00)
text_area.x = 20
text_area.y = 20

text_area2 = label.Label(font, text='IP: 192.168.30.89', color=0xFF0000)
text_area2.x = 20
text_area2.y = 50

text_area3 = label.Label(font, text='Press button <D1>', color=0x00FFFF)
text_area3.x = 20
text_area3.y = 105

text_area4 = label.Label(font, text='for Astrid Hotspot', color=0x00FFFF)
text_area4.x = 20
text_area4.y = 125

group = Group()
group.append(text_area)
group.append(text_area2)
group.append(text_area3)
group.append(text_area4)

display.root_group = group

while True:
    pass
