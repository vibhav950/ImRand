from sys import argv, exit
from warnings import warn as _warn
from cv2 import VideoCapture as _VideoCapture, cvtColor as _cvtColor, resize as _resize, threshold as _threshold
from cv2 import COLOR_BGR2HSV as _COLOR_BGR2HSV, COLOR_BGR2GRAY as _COLOR_BGR2GRAY, INTER_AREA as _INTER_AREA
from cv2 import THRESH_BINARY as _THRESH_BINARY, THRESH_OTSU as _THRESH_OTSU
from hashlib import sha512 as _sha512
from pyautogui import position as _position
from math import log as _log
from time import sleep as _sleep

class Random:
    def __init__(self, randengine: int = 0) -> None:
        """
        Used to initialize instances that dont share states.

        Optional parameter randengine can be set to explicitly select the underlying
        source of entropy for the generation of the internal seed; set to 0 by default.
        randengine = 0 : Image Based Randomness (IBR)
        randengine = 1 : Cursor Position Randomness (CPR)
        """
        if (randengine == 0):
            self._seed = self._get_random_seed_ibr(256)

        else:
            self._seed = self._get_random_seed_cpr()

    def _capture(self, port: int = 0):
        """
        Capture an image from the default port.
        """
        cam = _VideoCapture(port)
        result, img = cam.read()

        if not result:
            raise RuntimeError("port: failed to capture from selected/default port")

        img = _cvtColor(img, _COLOR_BGR2HSV)
        img = _cvtColor(img, _COLOR_BGR2GRAY)
        dimensions = (int(img.shape[1]*.05),int(img.shape[0]*.05))
        img = _resize(img, dimensions, interpolation=_INTER_AREA)
        ret_, bin_img = _threshold(img, 0, 255, _THRESH_BINARY+_THRESH_OTSU)
        cam.release()
        return bin_img

    def _get_random_seed_ibr(self, nbits: int) -> int:
        """
        Generate a random n-bit long seed, method is preferably called
        internally to ensure process-safe seed lengths.

        _capture() is called to capture an image; visual features and noise in
        the image positively affect the reliablility of the generator.
        
        Bits are picked from the image (converted to a bit-matrix) using the 
        non-linear Hénon map (with classical values a = 1.4 and b = 0.3);
        changing the coefficients is not recommended.
        """

        if not (1 <= nbits <= 512):
            raise ValueError("nbits: invalid bit length (expected 1 <= nbits <= 512)")
        
        bin_img = self._capture() // 255
        out = 0b0
        a, b = 1.4, 0.3
        x, y = nbits-1, nbits+1
        img_arr = bin_img.flatten()[:]
        N = len(img_arr)

        for _ in range(nbits):
            x, y = (1 - a*(x**2) + y)%N, b*x
            out = (out << 1) | int(img_arr[abs(int(x))])

        return out

    def _get_random_seed_cpr(self, nbytes: int = 16) -> int:
        """
        Capture cursor movement to generate random bits.

        Generate 16-32 random bytes; bits generated are always 
        grouped in octets (multiples of 8).
        """
        if not (16 <= nbytes <= 32):
            raise ValueError("nbytes: invalid byte length (expected 16 <= nbytes <= 32)")

        print("Move your cursor erratically without pausing till the progress bar reaches completion.")

        out = 0b0
        perc = 0
        for n_ in range(nbytes):
            state = 0b00000000
            for i in range(8):
                pos = _position()
                state = (state << 1) | ((pos[0] & 0b1) ^ (pos[1] & 0b1))
                _sleep(0.1)

                while (_position() == pos):
                    _sleep(0.2)

                perc = (n_*8 + i + 1)/(nbytes*8)
                print(f"Completed {int(perc * 100)}% [{'#'*int(perc*50)}{' '*(50 - int(perc*50))}]", end = "\r")

            out = (out << 8) | state

        out |= 1 << ((nbytes * 8) - 1)
        print()
        return out

    def get_nbits(self, nbits: int, enforce: bool = False) -> int:
        """
        Generate n random bits from a pre-set seed; may not necessarily return
        a n-bit integer.

        Updates the internal state on every call.
        
        If the optional argument enforce is set to True, the integer returned is
        strictly n-bits long.
        """

        if not (1 <= nbits <= 1024):
            raise ValueError("nbits: invalid bit length (expected 1 <= nbits <= 1024)")
        
        state = self._seed

        out = 0b0
        for _ in range(nbits):
            state = (state >> 1) | ((((state) ^ (state >> 1) ^ (state >> 2) ^ (state >> 7)) & 0b1) << 127)
            out = (out << 1) | (state & 0b1)

        if enforce:
            out |= (1 << (nbits-1))

        self._seed =  state
        return out

    def get_ranged_int(self, a: int, b: int) -> int:
        """
        Generate a random integer in the interval [a, b].

        _capture() is called to capture an image.

        [CAUTION!] this is an experimental method and not a good choice for
        generating multiple integers with small interval widths; this method
        will be deprecated in subsequent versions.
        """

        _warn('This feature is an\n'
              'experimental implementation and will be removed in a subsequent version.\n',
               DeprecationWarning, 2)

        if not ((a <= b) and (a >= 0) and (b >= 0)):
            raise ValueError("a, b: invalid range arguments (expected a <= b; a, b >= 0)")
        
        bin_img = self._capture()
        img_sha512_hash = _sha512(bin_img).hexdigest()
        img_int = int(img_sha512_hash, 16)

        rand_val = a + img_int % ((b-a)+1)
        return rand_val

    def get_ranged_ints(self, a: int, b: int, n: int) -> None:
        """
        Get n random integers in interval [a, b].

        Calls get_nbits() n times to obtain the ranged integers.
        """

        if not ((a <= b) and (a >= 0)):
            raise ValueError("a, b: invalid range arguments (expected a <= b; a, b >= 0)")
        
        width = b-a
        nbits = int(_log((width), 2)) + 1

        for _ in range(n):
            out = self.get_nbits(nbits, self._seed)
            rand_val = a + out % ((b-a)+1)
            print(rand_val)


def main():

    def usage_msg():
        msg = """
imrand v0.2 - August 16 2023

Usage: python imrand_2.py [mode] [options] [<value1> [<value2> [...]]]

Mode of operation:
            -IBR                    Image Based Randomness
            -CPR                    Cursor Position Randomness
General options:
            -h                      print this usage help and exit
            -nbits  <n>             generate n-bit random integer
            -range  <a> <b>         generate random int in the interval [a,b]
            -nrange <a> <b> <n>     generate n random ints in the interval [a,b]
            -[bin]                  binary output for nbits
        """
        print(msg)
        exit(1)

    if len(argv) <= 1 or (argv[1] == "-h" or argv[1] == "--help"):
        usage_msg()
    n = len(argv)

    if argv[1] == "-IBR":
        rand = Random()
    elif argv[1] == "-CPR":
        rand = Random(1)
    else:
        usage_msg()

    for i in range(2, n):
        if argv[i].lower() == "-range":
            try:
                a, b = int(argv[i+1]), int(argv[i+2])
            except ValueError:
                usage_msg()
            rand.get_ranged_ints(1, a, b)
            return
        
        if argv[i].lower() == "-nrange":
            try:
                a, b, n = int(argv[i+1]), int(argv[i+2]), int(argv[i+3])
            except ValueError:
                usage_msg()
            rand.get_ranged_ints(a, b, n)
            return

        if argv[i].lower() == "-nbits":
                try:
                    n = int(argv[i+1])
                except ValueError:
                    usage_msg()
                res = rand.get_nbits(n, enforce = True)
                
                if "-bin" in argv[2:n]: print(bin(res)[2:])
                else: print(res)
                

if __name__ == "__main__":
    main()
