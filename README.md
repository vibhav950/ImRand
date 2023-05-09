## imrand
# A tool to generate TRNGs using an image input.

# How to use
Use the -h option to view commands and options.

# How the random numbers are generated
This implementation uses two distinct approaches to generate a random number.

Method #1 (for the -range option)
A SHA512 hash of the input image is calculated which is an integer with a maximum value of 2^512 - 1. This integer is then reduced to one within the specified range using simple modular arithmetic.

Method #2 (for the -nbits option)
The image is resized and thresholded into a black-and-white format and converted to a stream of 0's and 1's, with the former and latter representing white and black pixels respectively. This array is then traversed in a chaotic manner using a non-linear function to gather the n bits.
