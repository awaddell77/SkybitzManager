from Dictify import *
from Dict_lst import *


#Created to add the customerid and shiptocode columns into the Dict_lst object data at runtime
#This was done because I didn't want us to be manually doing it excel.  

def load_csv(fname):
	f_data = Dict_lst(Dictify(fname).main())
	add_custid_and_shiptoid(f_data)
	return f_data

def add_custid_and_shiptoid(f_data):
	f_data.add_crit("ShipToId", '')
	f_data.add_crit("CustomerId",'')
	for i in range(0, len(f_data)):
		temp = f_data.get_index(i)
		temp['ShipToId'] = temp['ARDivisionNo'] + temp['CustomerNo'] + temp['ShipToCode']
		temp['CustomerId'] = temp['ARDivisionNo'] + temp['CustomerNo']



