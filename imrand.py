import sys
import cv2 as cv
import hashlib

def capture():
    cam = cv.VideoCapture(0)
    result, img = cam.read()
    if not result:
        return -1
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    print(img.shape)
    dimensions = (int(img.shape[1]*.05),int(img.shape[0]*.05))
    img = cv.resize(img, dimensions, interpolation=cv.INTER_AREA)
    ret_, bin_img = cv.threshold(img, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    cv.imshow('img', bin_img)
    cv.waitKey(0)
    cam.release()
    return bin_img

def rand_0(a, b, bin_img, bin_state):
    img_sha512_hash = hashlib.sha512(bin_img).hexdigest()
    img_int = int(img_sha512_hash, 16)

    rand_val = a + img_int%((b-a)+1)

    if bin_state == True:
        rand_val = str(bin(rand_val))
        print(rand_val[2:])
    else:
        print(rand_val)

def rand_1(n, bin_img, bin_state):
    if not (1 <= n <= 512):
        return -1
    
    bin_img = bin_img//255
    arr = ""
    a, b = 1.4, 0.3
    x, y = n-1, n+1
    img_arr = bin_img.flatten()[:]
    N = len(img_arr)

    for i in range(n):
        x, y = (1 - a*(x**2) + y)%N, b*x # chaotic Hénon map
        arr += str(int(img_arr[abs(int(x))]))
    arr = "1" + arr[1:]

    if bin_state == True:
        print(arr)
        return 1
    
    print(int(arr, 2))
    return 1

def main():
    def error_msg():
        print(f'''Usage: python {sys.argv[0]} [options]
  -h                      print this usage help and exit
  -nbits <bits>           generate n-bit random integer (max 512)
  -bin                    display in binary format
  -range <upper> <lower>  generate random integer in given range''')
        sys.exit(1)

    if len(sys.argv) <= 1 or (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        error_msg()
    n = len(sys.argv)

    bin_state = False
    if "-bin" in sys.argv[1:n]:
        bin_state = True

    for i in range(1, n):
        if sys.argv[i] == "-range":
            try:
                a, b = int(sys.argv[i+1]), int(sys.argv[i+2])
                res = rand_0(a, b, capture(), bin_state)
                if res == -1:
                    error_msg()
            except Exception:
                error_msg()

        elif sys.argv[i] == "-nbits":
            try:
                n = int(sys.argv[i+1])
                res = rand_1(n, capture(), bin_state)
                if res == -1:
                    raise Exception('not enough bits')
            except Exception:
                error_msg()

if __name__ == "__main__":
    main()