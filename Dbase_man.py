#sql server connection wrapper
import json, pyodbc

class Dbase_man:
	def __init__(self, conn_string):
		self.conn = pyodbc.connect(conn_string)
		self.cursor = self.conn.cursor()
	def close_conn(self):
		self.conn.close()
	
	def exec_query(self, query, retr = True ):
		rows = [[]]
		self.cursor.execute(query)
		if retr: rows = self.cursor.fetchall()
		else: self.cursor.commit()
		return rows


class Con_string:
	def __init__(self, Driver):
		pass