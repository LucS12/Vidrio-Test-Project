#Necessary Packages:import pandas as pd   #Needed to read in data into DataFrames & manipulate it#STEP 4. File paths for Mapping and Bank Activity files:mapping_path = 'Mapping/Cash_Rec_Mapping.xlsx'    bank_activity_path = 'Settled Cash Activity Statement - Vidrio_22 Jul 2022.xls'#STEP 4. Read  Mapping file & Bank Activity file into DataFrames:    mapping_df = pd.read_excel(mapping_path)            #Mapping DataFrameactivity_df = pd.read_excel(bank_activity_path)     #Bank Activity DataFrame#STEP 5. Replacing any NaNs on Bank Activity DataFrame with blank strings "":activity_df.fillna("", inplace=True)#STEP 6. Creating blank DataFrame to hold exceptions:exceptions_df = pd.DataFrame()#STEP 7. Boolean variable to track if there are exceptions (initially False):exception_exists = False#STEP 8. Adding Named Columns to Bank Activity DataFrame:  #New 'Bank Reference ID' column equal to original 'Reference Number' column:activity_df['Bank Reference ID'] = activity_df['Reference Number']    #New 'Post Date' column equal to original 'Cash Post Date' column (date format):activity_df['Post Date'] = pd.to_datetime(activity_df['Cash Post Date'])       #New 'Amount' column equal to original 'Transaction Amount Local' column:activity_df['Amount'] = activity_df['Transaction Amount Local']  #New 'Description column equal to a combo of the original transaction   # description columns shown in the list below:desc_cols = ['Transaction Description 1','Transaction Description 2',              'Transaction Description 3', 'Transaction Description 4',             'Transaction Description 5', 'Transaction Description 6',             'Detailed Transaction Type Name', 'Transaction Type']  #Separate each description with a space for readability:activity_df['Description'] = activity_df[desc_cols].T.agg(' '.join)  #New 'Bank Account' column equal to original 'Cash Account Number' column:activity_df['Bank Account'] = activity_df['Cash Account Number']  #New 'Closing_Balance' column equal to original 'Closing Balance Local' column:activity_df['Closing_Balance'] = activity_df['Closing Balance Local']  #New 'Filename' column equal to original 'Cash Account Number' column plus the  # current date and time plus '.csv' formatted as a string:      