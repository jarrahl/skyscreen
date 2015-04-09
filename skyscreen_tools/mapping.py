import numpy as np
from skyscreen_core.interface import Screen


class MappingOver(object):
	def __init__(self, domain, location_transform, color_transform):
		"""
		:param domain: a matrix, of form:
			[ top left row, top left col ]
		    [ bottom r row, bottom r col ]
		:param location_transform:
			A mapping matrix L. For each point Pl, we calculate
			a destination as Pl . L
			Pl is a vector of length 2, L has size 2x2
		:param point_transform
			A color transform matrix C. For each point Pc, we calculate
			a new destination value as Pc . C
			Pc is a vector of length 3, in order R, G, B.
			C has size 3x3
		:return:
		"""
		assert isinstance(domain, np.ndarray)
		assert isinstance(location_transform, np.ndarray)
		assert isinstance(color_transform, np.ndarray)
		assert domain.shape == (2, 2)
		assert location_transform.shape == (2, 2)
		assert color_transform.shape == (3, 3)
		self.n_location_transform = location_transform
		self.n_color_transform= color_transform

		self.topleft_row = domain[0, 0]
		self.topleft_col = domain[0, 1]
		self.bottomright_row = domain[1, 0]
		self.bottomright_col = domain[1, 1]
		assert 0 <= self.topleft_row < self.bottomright_row < Screen.screen_rows, \
			'not 0 <= topleft row: %d and bottomright row %d < %d' % \
			(self.topleft_row, self.bottomright_row, Screen.screen_rows)
		assert 0 <= self.topleft_col < self.bottomright_col < Screen.screen_cols, \
			'not 0 <= topleft col: %d and bottomright col %d < %d' % \
			(self.topleft_col, self.bottomright_col, Screen.screen_cols)

	def numpy_fn(self, input):
		sub_slice = input[self.topleft_row:self.bottomright_row,
					      self.topleft_col:self.bottomright_col]
		transformed_space = self.build_transformed_space()
		transform_input = np.concatenate([transformed_space, sub_slice], axis=2)
		full_transform = self.construct_full_transform()
		transformed_result = np.round(np.dot(transform_input, full_transform)).astype(int)
		self.apply_transform(transformed_result, input)

	def apply_transform(self, transformed, input):
		num_rows = self.bottomright_row-self.topleft_row
		num_cols = self.bottomright_col-self.topleft_col
		assert transformed.shape == (num_rows, num_cols, 3)
		transformed.resize((num_rows*num_cols, 5))
		# This loop is a problem. Port to cython
		xs = transformed[:, 0]
		ys = transformed[:, 1]
		colors = transformed[:, 2:]
		# This part may be a problem... We'll see!
		input[xs, ys] = colors


	def construct_full_transform(self):
		full_transform = np.zeros((5,5))
		full_transform[0:2, 0:2] = self.n_location_transform
		full_transform[2:5, 2:5] = self.n_color_transform
		return full_transform

	def build_transformed_space(self):
		num_rows = self.bottomright_row - self.topleft_row
		num_cols = self.bottomright_col - self.topleft_col
		px_row = np.linspace(self.topleft_row,
							 self.bottomright_row,
							 num_rows,
							 endpoint=False)
		px_rows = np.resize(px_row, (num_cols, num_rows)).T
		px_col = np.linspace(self.topleft_col,
							 self.bottomright_col,
							 num_cols,
							 endpoint=False)
		px_cols = np.resize(px_col, (num_rows, num_cols))
		result = np.zeros((num_rows, num_cols, 2))
		result[:, :, 0] = px_rows
		result[:, :, 1] = px_cols
		return result
