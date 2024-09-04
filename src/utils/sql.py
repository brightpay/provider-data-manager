import os
import json
import boto3
import pymysql
import datetime
from decimal import Decimal


lambda_client = boto3.client('lambda')
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client('s3')
sr = boto3.resource('s3')
kms = boto3.client('kms')
rds = boto3.Session().client('rds')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

def get_current_time():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
	
    return datetime.datetime.now().strftime("%Y-%m-%d")

def execute_query(sql_query, sql_query_params = None, insert_multiple = None):

	# token = rds.generate_db_auth_token(os.environ['rds_host'], 3306, os.environ['rds_user'], Region='ap-southeast-1')

	#Connecting to RDS using token
	rds_conn = pymysql.connect(
		host=os.environ['rds_host'],
		port=3306,
		user=os.environ['rds_user'],
		passwd=os.environ['rds_pwd'],
		db=os.environ.get('rds_database','unity'),
		ssl={'ca': 'rds-combined-ca-bundle.pem'},
		autocommit=True,
		charset='utf8'
	)
	rds_cursor = rds_conn.cursor(pymysql.cursors.DictCursor)

	if insert_multiple:
		for sql_query_param in sql_query_params:
			try:
				rds_cursor.execute(sql_query % sql_query_param)
			except Exception as e:
				print('error','Error in inserting row',e)
				print('error',"Row:", sql_query_param)

	elif sql_query_params:
		print('info','sql_query_params :-',sql_query_params)
		rds_cursor.execute(sql_query,(','.join(sql_query_params)))
	else:
		sql_query = sql_query.replace("'None'","NULL").replace("'NULL'","NULL").replace("'Null'","NULL").replace("Null","NULL").replace("None","NULL")
		#print ("Execute SQL Query:",sql_query)
		rds_cursor.execute(sql_query)

	sql_result = []
	if insert_multiple:
		pass
	else:
		for record in rds_cursor:
			sql_result.append(record)

	rds_cursor.close()
	rds_conn.close()

	return sql_result

def bulk_insert(table, records):

	#records should be a list of dictionaries
	insert_string = None
	if len(records) > 0:
		for _rec in records:

			insert_item = "('" + "','".join([str(_rec[_k]) for _k in list(_rec.keys())]) + "')"

			if insert_string:
				insert_string += ',' + insert_item
			else:
				insert_string = insert_item

		insert_string = "INSERT INTO " + table + " (" + ','.join(list(records[0].keys())) + ") VALUES " + insert_string + ";"
		# customLog('Verbose','Bulk Insert Query', insert_string)
		insert_query_response = execute_query(insert_string)
		print('Info','Bulk Insert Response', insert_query_response)
		return insert_query_response
	else:
		print('Error','Empty record set for SQL Bulk Insert')

def log(data, database, table, sublog_table=None, sublog_data=[]):
	log_data = {
		'destination_database': 'mysql_' + database,
		'destination_table': table,
		'data': data,
		'logger': 'unity'
	}
	if sublog_table:
		if len(sublog_data) > 0:
			log_data.update({'sub_logging': []})
			for sublog_record in sublog_data:
				log_data['sub_logging'].append({
						'destination_database': 'mysql_' + database,
						'destination_table': sublog_table,
						'data': sublog_record
					})
	lambda_client.invoke(FunctionName='sherlock_pixel',
		    InvocationType='Event',
		    Payload=json.dumps(log_data))
	return