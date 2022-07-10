from support.detect import detect
import sys

mode = detect(sys.argv[2])

print(mode)

# call particular strategy acording to mode