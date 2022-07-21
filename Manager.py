from Dbase_man import Dbase_man
import datetime
from datetime import timezone
from loadJson import loadJson
from Dict_lst import Dict_lst
import Dictify, sbcsv

#in the future it will be a thread 
creds = loadJson('credentials.json')

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"  # Just an Example (SQL2008-2018)
    +"Server={0};".format(creds['server']) # Here you insert you servername
    +"Database={0};".format(creds['database']) # Here you insert your db Name
    +"UID={0};".format(creds['username']) # Here you insert the SQL User to auth
    +"PWD={0};".format(creds['password']) # Here you insert the User's password
    )

class Manager:
	def __init__(self,db_conn):
		#commented out for testing
		#if not isinstance(db_conn, Dbase_man): raise TypeError("Must be Dbase_man")
		self.db_conn = Dbase_man(db_conn)
		self.sess_time = datetime.datetime.now(timezone.utc).isoformat()
		self.log_fname= self.sess_time.split('T')[0].replace('-','') + 'T'+ self.sess_time.split('T')[1].replace(':','-') + ".txt"
		self.cust_list = []

		

	def run(self):
		pass
	def deactivate_ship_tos(self, fname):
		ship_to_lst = sbcsv.load_csv(fname)
		deact_col = "De-activated in skybitz?"
		ship_to_lst.add_crit(deact_col,'')
		for i in range(0,len(ship_to_lst)):
			temp = ship_to_lst.get_index(i)
			res = self.db_conn.exec_query("SELECT SLCust_ShipToZip FROM SLCustomerShipTo WHERE  SLCust_ShipToId = \'{0}\' AND SLCust_ShipToZip IS NOT NULL AND SLCust_ShipToCity IS NOT NULL  ".format(temp['ShipToId']))
			if not res: temp[deact_col] = "No. Could not be found"
			else: 
				customer_no, ship_to_code, corporate_id, company_id, division_id, user_id, module_id, s_datetime,inactive_region, inactive_territory = temp['CustomerId'], temp['ShipToId'],  '001', "000", "000","ADMINISTRATOR",4,'', 9,35
				self._deactivate_ship_to(customer_no, ship_to_code, corporate_id, company_id, division_id, user_id, module_id, s_datetime, inactive_region, inactive_territory)
		ship_to_lst.export()
		#print(ship_to_lst)




	def _deactivate_ship_to(self,customer_no, ship_to_code, corporate_id, company_id, division_id, user_id, module_id, s_datetime, inactive_region, inactive_territory):
		Product_Tax_Fee_back_up = []


		#insert row into audit trail
		audit_f_desc = "Modified {0} {1}".format(customer_no, ship_to_code)
		err_desription= ""
		#print(self._insert_audit_trail(corporate_id, company_id, division_id, user_id, module_id, s_datetime, audit_f_desc, err_desription))
		audit_trail_query = self._insert_audit_trail(corporate_id, company_id, division_id, user_id, module_id, s_datetime, audit_f_desc, err_desription)
		self._wrt_shipto_log(customer_no, ship_to_code, audit_trail_query)
		self.db_conn.exec_query(audit_trail_query, False)
		#updates SLCustomerShipTo table
		customer_ship_to_query = "UPDATE SLCustomerShipTo SET SLCust_ShipToStatus = \'C\' WHERE SLCust_ShipToCustomerId =\'{0}\' AND SLCust_ShipToId = \'{1}\'".format(customer_no, ship_to_code)
		self._wrt_shipto_log(customer_no, ship_to_code, customer_ship_to_query)
		self.db_conn.exec_query(customer_ship_to_query, False)
		#print(customer_ship_to_query	)
		#deletes all records associated with the customer and ship-to in the in the SLCustomershiptoProdutTaxFee table
		Product_Tax_Fee_back_up_query	= "SELECT * FROM  SLCustomerShipToProductTaxFee WHERE ( SLSPTF_CustomerID = \'{0}\' ) and ( SLSPTF_ShipToId = \'{1}\' )".format(customer_no, ship_to_code)
		#Product_Tax_Fee_back_up	= self.db_conn.exec_query(Product_Tax_Fee_back_up_query)
		#actually deletes rows from SLCustomershiptoProdutTaxFee table
		product_tax_fee_deletion_query = "DELETE FROM SLCustomerShipToProductTaxFee	 WHERE ( SLSPTF_CustomerID = \'{0}\') AND ( SLSPTF_ShipToId = \'{1}\')".format(customer_no, ship_to_code)
		self._wrt_shipto_log(customer_no, ship_to_code, product_tax_fee_deletion_query)
		self.db_conn.exec_query(product_tax_fee_deletion_query, False)
		#print(product_tax_fee_deletion_query)
		#adds rows to SLCustomerShipToProductTaxFee with null taxfeeprofileid values
		products = self._get_unique_products()
		for i in range(0, len(products)):
			product_q = "INSERT into SLCustomerShipToProductTaxFee ( SLSPTF_CorporateId, SLSPTF_CompanyId, SLSPTF_DivisionId, SLSPTF_CustomerId, SLSPTF_ShipToId, SLSPTF_ProductId, SLSPTF_TaxFeeProfileId ) " \
			" VALUES ( \'{0}\', \'{1}\', \'{2}\', \'{3}\', \'{4}\', \'{5}\', null )".format(corporate_id, company_id, division_id, customer_no, ship_to_code, products[i] )
			self._wrt_shipto_log(customer_no, ship_to_code, product_q)
			self.db_conn.exec_query(product_q, False)
		#deletes all associated records in the SLCustomerShipToProductPrice  
		prod_price_delete_query = "DELETE FROM SLCustomerShipToProductPrice WHERE SLSPP_ShipToId = \'{0}\' AND SLSPP_CustomerID = \'{1}\'".format(ship_to_code, customer_no)
		
		self._wrt_shipto_log(customer_no, ship_to_code,prod_price_delete_query)
		self.db_conn.exec_query(prod_price_delete_query, False)

		#inserts new productprice rows with null values
		for i in range(0, len(products)):
			prod_price_insert_q = "INSERT INTO SLCustomerShipToProductPrice VALUES (\'{0}\',\'{1}\',\'{2}\',\'{3}\',\'{4}\',\'{5}\',NULL,0.0000,0.00)".format(corporate_id, company_id, division_id, ship_to_code, customer_no, products[i])
			self._wrt_shipto_log(customer_no, ship_to_code,prod_price_insert_q)
			self.db_conn.exec_query(prod_price_insert_q, False)
			
		#get shiptoregions
		shipto_regions = self._get_cust_shipto_regions(customer_no, ship_to_code)

		shipto_region_delete_query = "DELETE FROM SLCustomerShipToRegion WHERE SLCSR_ShipToId = \'{0}\' AND SLCSR_CustomerId = \'{1}\'".format(ship_to_code, customer_no)
		self._wrt_shipto_log(customer_no, ship_to_code,shipto_region_delete_query)
		self.db_conn.exec_query(shipto_region_delete_query, False)

		shipto_region_insert_query = "INSERT INTO SLCustomerShipToRegion" \
			" VALUES  (\'{0}\',\'{1}\',\'{2}\',\'{3}\',\'{4}\',{5},{6},{7})".format(corporate_id, company_id, division_id, customer_no, ship_to_code, inactive_region, inactive_territory, 1)
		self._wrt_shipto_log(customer_no, ship_to_code,shipto_region_insert_query)
		self.db_conn.exec_query(shipto_region_insert_query,False)
		#deletes all rows that are associated with the shipto and customer id in SLCustomerShipToProductDefault 
		product_default_delete_query = "DELETE FROM SLCustomerShipToProductDefault WHERE [SLSPD_ShipToId]=\'{0}\' and SLSPD_CustomerID = \'{1}\'".format(ship_to_code, customer_no)
		#print(product_default_delete_query)
		self._wrt_shipto_log(customer_no, ship_to_code,product_default_delete_query)
		self.db_conn.exec_query(product_default_delete_query, False)


	def _get_unique_products(self):
		cmd = "SELECT SLP_Id FROM SLProduct GROUP BY SLP_Id ORDER BY SLP_Id"
		product_ids = self.db_conn.exec_query(cmd)
		if product_ids:
			return [p_ids[0] for p_ids in product_ids]
		return [[]]
	def _get_cust_shipto_regions(self, customer_no, ship_to_code):
		res = []
		cmd = "SELECT sr.SLCSR_CompanyId, sr.SLCSR_CorporateId, sr.SLCSR_DivisionId, sr.SLCSR_RegionId, sr.SLCSR_TerritoryId, sr.SLCSR_Primary"\
		" FROM SLCustomerShipToRegion sr WHERE sr.SLCSR_CustomerId = \'{0}\'  AND sr.SLCSR_ShipToId = \'{1}\'".format(customer_no, ship_to_code)
		res= self.db_conn.exec_query(cmd)
		return res
	def _wrt_shipto_log(self, customer_no, ship_to_code, msg):
		with open(self.log_fname, 'a') as sfile:
			sfile.writelines(customer_no + '|' + ship_to_code +  '|' + msg + '\n')



	def _audit_trail_datetime(self):
		#this is here because it looks too messy inside of the insert_audit_trail method
		the_now = datetime.datetime.now()
		second_suffix = ".000"
		year = str(the_now.year)
		month = str(the_now.month).zfill(2)
		day = str(the_now.day).zfill(2)
		hour = str(the_now.hour).zfill(2)
		minute = str(the_now.minute).zfill(2)
		second = str(the_now.second).zfill(2)+ second_suffix	
		am_pm = "AM" if the_now.hour < 12 else "PM"
		return  "{0}/{1}/{2} {3}:{4}:{5} {6}".format(month, day, year, hour, minute, second, am_pm)


	def _insert_audit_trail(self, corporate_id, company_id, division_id, user_id, module_id, s_datetime , funtion_desc, err_desription):
		#corporate_id, company_id, division_id, user_id, module_id, s_datetime, funtiondesc, err_desription = str(corporate_id), str(company_id), str(division_id), 
		n_datetime = s_datetime if s_datetime != '' else self._audit_trail_datetime()
		query = "INSERT INTO SLAuditTrail(SLAudit_CorporateId, SLAudit_CompanyId, SLAudit_DivisionId, SLAudit_UserID, SLAudit_ModuleId, SLAudit_DateTime, SLAudit_FunctionDesc, SLAudit_ErrDescription) VALUES"
		values = "(\'{0}\', \'{1}\', \'{2}\', \'{3}\', {4}, \'{5}\', \'{6}\', \'{7}\')".format(str(corporate_id), str(company_id), division_id, user_id, module_id, n_datetime, funtion_desc, err_desription)
		return query + values


db_conn = conn_str
m_test = Manager(db_conn)
#h = m_test._insert_audit_trail( '001','000','000','ADMINISTRATOR',4,'','Modified 010099151 010099151TORD','')
#customer_no, ship_to_code, corporate_id, company_id, division_id, user_id, module_id, s_datetime,inactive_region, inactive_territory = "010060010", "010060010HWY",  '001', "000", "000","ADMINISTRATOR",4,'', 8,34
#h = m_test._deactivate_ship_to(customer_no, ship_to_code, corporate_id, company_id, division_id, user_id, module_id, s_datetime, inactive_region, inactive_territory)
m_test.deactivate_ship_tos("allshiptos.csv")
m_test.db_conn.close_conn()

#m_test._wrt_shipto_log(customer_no, ship_to_code, "testing")