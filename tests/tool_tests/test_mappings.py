import skyscreen_tools.mapping as mapping
import numpy as np


def quick_init():
	domain = np.array([[1, 5], [11, 13]])
	location_transform = np.random.random(size=(2, 2))
	color_transform = np.random.random(size=(3, 3))
	return mapping.MappingOver(domain, location_transform, color_transform)


def test_init():
	quick_init()


def test_space_build():
	mapping = quick_init()
	transformed_space = mapping.build_transformed_space()
	for r in xrange(mapping.bottomright_row, mapping.topleft_row):
		for c in xrange(mapping.bottomright_col, mapping.topleft_col):
			assert transformed_space[r, c, 0] == r, '%d was not %d' % (transformed_space[r, c, 0], r)
			assert transformed_space[r, c, 1] == c, '%d was not %d' % (transformed_space[r, c, 1], c)


def test_transform_construction_single():
	mapping = quick_init()
	transform = mapping.construct_full_transform()

	point = np.random.random(2)
	color = np.random.random(3)

	full_vec = np.concatenate([point, color])

	got = np.dot(transform, full_vec)
	expected_position = np.dot(mapping.n_location_transform, point)
	expected_color = np.dot(mapping.n_color_transform, color)
	print got
	print expected_position, expected_color
	assert np.all(got[0:2] == expected_position)
	assert np.all(got[2:5] == expected_color)


def test_transform_construction_multiple():
	mapping = quick_init()
	transform = mapping.construct_full_transform()

	point = np.random.random((2, 100))
	color = np.random.random((3, 100))

	full_vec = np.concatenate([point, color])

	got = np.dot(transform, full_vec)
	expected_position = np.dot(mapping.n_location_transform, point)
	expected_color = np.dot(mapping.n_color_transform, color)
	assert np.all(got[0:2] == expected_position)
	assert np.all(got[2:5] == expected_color)

def test_apply_transform():
	mapping = quick_init()
	transformed = np
	mapping.apply_transform()