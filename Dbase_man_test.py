#sql server connection wrapper
import json, pyodbc

class Dbase_man:
	def __init__(self, conn_string):
		self.conn = pyodbc.connect(conn_string)
		self.cursor = self.conn.cursor()
	def close_conn(self):
		self.conn.close()
	
	def exec_query(self, query):
		if "DELETE" in query.upper() or "UPDATE" in query.upper() or "INSERT" in query.upper(): return [[query]]
		else:
			self.cursor.execute(query)
			rows = self.cursor.fetchall()
			return rows

		#return [[i for i in range(0, 10)] for j in range(0, 100)]


class Con_string:
	def __init__(self, Driver):
		pass