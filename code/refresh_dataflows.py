import argparse
import logging
import msal
import dataflow_pbi_refresh_api as df_api


def init_argparse():
	parser = argparse.ArgumentParser(description='Tool for automate the refresh of your Power BI dataflows and datasets. This tool use an Azure AD App for login.')
	parser.add_argument('-t', '--tenantId', required=True, help='Yout tenant ID.')
	parser.add_argument('-c', '--clientId', required=True, help='The client ID for login on yout Azure AD app.')
	parser.add_argument('-s', '--secretKey', required=True, help='The secret key for login on yout Azure AD app.')
	# parser.add_argument('-r', '--refresh', choices=['all', 'dataflows', 'datasets'], default='all', required=False, help='Choose what will be refreshed.')
	parser.add_argument('-w', '--workspace', required=False, help='The workspace ID that contains your dataflows or your datasets. If is empty, process will look up workspaces where it has permissions.')
	# parser.add_argument('-df', '--dataflow', required=False, help='Dataflow ID to refresh. If is empty, process will refresh all dataflows that it can.')
	# parser.add_argument('-ds', '--dataset', required=False, help='Dataset ID to refresh. If is empty, process will refresh all datasets that it can.')
	# parser.add_argument('-l', '--log', choices=[])
	return parser


if __name__ == '__main__':

	logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(levelname)s:%(message)s')
	
	print("Starting...")
	parser = init_argparse()

	args = parser.parse_args()

	url = 'https://login.microsoftonline.com/' + args.tenantId
	app = msal.ConfidentialClientApplication(client_id = args.clientId, authority = url, client_credential = args.secretKey)
	workspace_id = args.workspace

	dataflows = df_api.get_dataflows(app, workspace_id)

	for dataflow in dataflows:
		# CONTROLAR cuando de un error al actualizar el dataflow.
		df_api.refresh_dataflow(app, workspace_id, dataflow.get('objectId'))


	df_api.check_dataflows_refresh(app, workspace_id, dataflows)
	print(dataflows)


"""
1. App
- Get workspaces
2. Get dataflows & their data
3. Update dataflows
4. Check dataflows
5. Get datasets & their data
6. Update datasets
7. Check datasets
"""
