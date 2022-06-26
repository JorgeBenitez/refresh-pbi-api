import requests
import json
import logging
from decorators import retry

url_api = 'https://api.powerbi.com/v1.0/myorg/groups/'
scope = ['https://analysis.windows.net/powerbi/api/.default'] 

##########
# AÑADIR RETRY???
def get_token(app, scope):

	# Looking for a token in cache
	result = None
	result = app.acquire_token_silent(scope, account=None)

	if not result:
		# Token doesn't exist in cache. Generate new token.
		result = app.acquire_token_for_client(scopes=scope)

	if 'access_token' in result:
		return(result['access_token'])
	else:
		##########
		# LANZAR ALGÚN TIPO DE EXCEPCIÓN????
		print("Error getting access token:", result.get("error"), result.get("error_description"))


@retry(5, 3)
def get_dataflows(app, workspace_id):
	
	token = get_token(app, scope)
	headers = {'Authorization': f'Bearer {token}'}
	response = requests.get(url_api + workspace_id + "/dataflows", headers=headers)
	
	if response.status_code == 200:
		response_json = json.loads(response.content)
		dataflows = []
	
		for value in response_json.get('value'):
			dataflow_transactions = get_dataflow_transactions(app, workspace_id, value.get('objectId'))


			dataflows.append(
				{
					'objectId' : value.get('objectId'),
					'name' : value.get('name')
				} | dataflow_transactions
			)

		return dataflows
	
	else:
		return None


def get_dataflow_transactions(app, workspace_id, dataflow_id):

	token = get_token(app, scope)
	headers = {'Authorization': f'Bearer {token}'}
	response = requests.get(url_api + workspace_id + "/dataflows/" + dataflow_id + "/transactions", headers=headers)
	
	if response.status_code == 200:
		response_json = json.loads(response.content)

		return 	{
					'objectId' : dataflow_id,
					'status' : response_json.get('value')[0].get('status'),
					'refreshDate' : response_json.get('value')[0].get('endTime')
				}
	
	else:
		return None


def refresh_dataflow(app, workspace_id, dataflow_id):

	token = get_token(app, scope)
	headers = {'Authorization': f'Bearer {token}'}
	data = {
	  "notifyOption": "NoNotification" # MailOnFailure
	}
	response = requests.post(url_api + workspace_id + "/dataflows/" + dataflow_id + "/refreshes?processType=default",
		                    data=data, headers=headers)
    
    # if response.status_code != 200:
    #     logging.error(f'Cannot refresh dataflow with ID: {dataflow_id}. {response}')

	return (response.content if response.status_code != 200 else None)


@retry(10, 12) # every 10 seconds until 120.
def check_dataflows_refresh(app, workspace_id, dataflows):
	# This method will add is_refreshed atribute to dataflows

	for dataflow in dataflows:

		refresh_data = get_dataflow_transactions(app, workspace_id, dataflow.get('objectId'))
		
		if refresh_data != None and refresh_data.get('status') == "Success" and \
			 refresh_data.get('refreshDate') >= dataflow.get('refreshDate'):
			dataflow['is_refreshed'] = True
			# dataflow['refreshDate'] = refresh_data.get('refreshDate')
		else:
			dataflow['is_refreshed'] = False

        
	logging.info("Dataflows status: " + str(dataflows))	
	
	are_all_refreshed = all(dataflow.get('is_refreshed') is True for dataflow in dataflows)

	return are_all_refreshed
