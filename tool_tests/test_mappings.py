import skyscreen_tools.mapping as mapping
import numpy as np

def quick_init():
	domain = np.array([[1, 5], [11, 13]])
	location_transform = np.random.random(size=(2,2))
	color_transform = np.random.random(size=(3,3))
	return mapping.MappingOver(domain, location_transform, color_transform)

def test_init():
	quick_init()

def test_space_build():
	mapping = quick_init()
	transformed_space = mapping.build_transformed_space()
	print transformed_space
	assert False