

class BulkInsert:
	def __init__(self, table, columns):
		self.table = str(table)
		self.columns = list(columns)
		self.values = []
	def add_value_row(self, val_row):
		if not isinstance(val_row, list): raise TypeError("Must be list")
		#TODO: Make a custom exception for the runtimeerror below
		if len(self.columns) != len(val_row): raise RuntimeError("Column/Value Row Mismatch")

		self.values.append("(" + ', '.join(val_row) + ")")
	def _construct_values(self):
		for i in range(0, len(self.values)):
			temp = '('
	def _construct_query(self):



