import xlsxwriter
import json

# Output File
file_name = "Suprabhat_APIs_v4.xlsx"

def create_xlsx_no_pandas():
    # Data Structures
    apis_headers = [
        "Ref ID", "Module/Feature", "API Name", "HTTP Method", "Endpoint URL", 
        "Headers Required", "Request Payload (JSON example)", "URL Params", 
        "Expected Response (Success)", "Token Variable", "Is Token Generator", "Auth Scope"
    ]
    
    apis_data = [
        [
            "AUTH-001", "Authentication", "Get Auth Token", "POST", "getAuthToken",
            "Content-Type: application/x-www-form-urlencoded",
            json.dumps({
                "login.username": "invoice2",
                "login.password": "vst123",
                "tenantId": "suprabhat-latest"
            }),
            "", # URL Params
            '{"token": "<authToken>"}', "authToken", "TRUE", ""
        ],
        [
            "CUST-001", "Customer", "Get Customer Profile Details", "GET", "getCustomerProfileDetails",
            "token: {{authToken}}",
            "", # Payload
            json.dumps({
                "Key": "",
                "tenantId": "suprabhat-latest",
                "customerId": "20955",
                "supplierId": "HERITAGE",
                "facilityId": "20955"
            }),
            "", "", "FALSE", ""
        ]
    ]

    env_headers = ["Variable", "Value"]
    env_data = [
        ["base_url", "https://master.suprabhatapp.in/rest/suprabhat/V2"],
        ["tenantId", "suprabhat-latest"]
    ]

    print(f"Creating {file_name} using pure xlsxwriter...")
    
    try:
        workbook = xlsxwriter.Workbook(file_name)
    except IOError as e:
        if e.errno == 13:
            print(f"WARNING: '{file_name}' is open. Saving to '{file_name.replace('.xlsx', '_new.xlsx')}' instead.")
            file_name = file_name.replace('.xlsx', '_new.xlsx')
            workbook = xlsxwriter.Workbook(file_name)
        else:
            raise e
    
    # --- Sheet 1: apis ---
    worksheet = workbook.add_worksheet("apis")
    # Write Headers
    for col_num, header in enumerate(apis_headers):
        worksheet.write(0, col_num, header)
    # Write Data
    for row_num, row_data in enumerate(apis_data, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_data)
            
    # --- Sheet 2: environments ---
    worksheet_env = workbook.add_worksheet("environments")
    # Write Headers
    for col_num, header in enumerate(env_headers):
        worksheet_env.write(0, col_num, header)
    # Write Data
    for row_num, row_data in enumerate(env_data, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet_env.write(row_num, col_num, cell_data)

    workbook.close()
    print("Success! File created.")

if __name__ == "__main__":
    try:
        create_xlsx_no_pandas()
    except ImportError:
        print("CRITICAL: xlsxwriter not installed. Run 'pip install xlsxwriter'")
    except Exception as e:
        print(f"Error: {e}")

