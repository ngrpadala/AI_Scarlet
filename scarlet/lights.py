import board
import neopixel

PIXEL_PIN  = board.D18
NUM_PIXELS = 24
BRIGHTNESS = 0.3
ORDER      = neopixel.GRB

pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

def show_status(effect):
    colors = {
        "listening": (50,100,255),
        "thinking":  (255,120,30),
        "speaking":  (255,20,127),
        "error":     (255,0,0),
        "idle":      (0,0,0),
    }
    pixels.fill(colors.get(effect, (0,0,0)))
    pixels.show()

def clear_ring():
    pixels.fill((0,0,0))
    pixels.show()
