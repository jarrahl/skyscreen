import random
import os

patterns = [
	"eye-of-god",
	"fermat-spiral",
	"gradients-fast",
	"gradients-slow",
	"gradients-perlin",
	"kaleidoscope-bubbles",
	"kaleidoscope-circles",
	"kaleidoscope-combined",
	"kaleidoscope-flowers",
	"kaleidoscope-snake",
	"kaleidoscope-squares",
	"kaleidoscope-superfast",
	"kaleidoscope-triangles",
	"lewis",
	"npnoise",
	"perlin-kaleido-pinksky",
	"perlin-kaleido-spaceclouds",
	"perlin-kaleido-spaceribbons",
	"perlin-kaleido-supernova",
	"perlin-kaleido-bloom",
	"perlin-kaleido-cytoplasm",
	"perlin-kaleido-persian",
	"perlin-kaleido-bottles",
	"perlin-pinksky",
	"perlin-spaceclouds",
	"perlin-spaceribbons",
	"perlin-supernova",
	"sinwaves",
	"stars",
	"text"
]

p1 = random.choice(patterns)
p2 = random.choice(patterns)
op = random.choice(["and", "or", "xor", "avg", "max", "diff", "sum", "behind"])
print p1, op, p2
call_args = ["python", "patterns", "combine"]
os.execvp("python", call_args + [p1, op, p2])
