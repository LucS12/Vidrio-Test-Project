#Necessary Packages:
import pandas as pd   #Needed to read in data into DataFrames & manipulate it
import datetime       #Used to get the current date and time

#STEP 4. File paths for Mapping and Bank Activity files:
mapping_path = 'Mapping/Cash_Rec_Mapping.xlsx'    
bank_activity_path = 'Settled Cash Activity Statement - Vidrio_22 Jul 2022.xls'

#STEP 4. Read  Mapping file & Bank Activity file into DataFrames:    
mapping_df = pd.read_excel(mapping_path)            #Mapping DataFrame
activity_df = pd.read_excel(bank_activity_path)     #Bank Activity DataFrame

#STEP 5. Replacing any NaNs on Bank Activity DataFrame with blank strings "":
activity_df.fillna("", inplace=True)

#STEP 6. Creating blank DataFrame to hold exceptions:
exceptions_df = pd.DataFrame()

#STEP 7. Boolean variable to track if there are exceptions (initially False):
exception_exists = False

#STEP 8. Adding Named Columns to Bank Activity DataFrame:
  #New 'Bank Reference ID' column equal to original 'Reference Number' column:
activity_df['Bank Reference ID'] = activity_df['Reference Number']  

  #New 'Post Date' column equal to original 'Cash Post Date' column (date format):
activity_df['Post Date'] = pd.to_datetime(activity_df['Cash Post Date'])    

  #New 'Value Date' column equal to original 'Cash Value Date' column (date format):
activity_df['Value Date'] = pd.to_datetime(activity_df['Cash Value Date'])      
 
  #New 'Amount' column equal to original 'Transaction Amount Local' column:
activity_df['Amount'] = activity_df['Transaction Amount Local']

  #New 'Description column equal to a combo of the original transaction 
  # description columns shown in the list below:
desc_cols = ['Transaction Description 1','Transaction Description 2', 
             'Transaction Description 3', 'Transaction Description 4',
             'Transaction Description 5', 'Transaction Description 6',
             'Detailed Transaction Type Name', 'Transaction Type']

  #Separate each description with a space for readability:
activity_df['Description'] = activity_df[desc_cols].T.agg(' '.join)

  #New 'Bank Account' column equal to original 'Cash Account Number' column:
activity_df['Bank Account'] = activity_df['Cash Account Number']

  #New 'Closing_Balance' column equal to original 'Closing Balance Local' column:
activity_df['Closing_Balance'] = activity_df['Closing Balance Local']

  #New 'Filename' column equal to original 'Cash Account Number' column plus the
  # current date and time plus '.csv' formatted as a string:
cash_acct_num = activity_df['Cash Account Number'].apply(str)         #Turning int column into string
date_time_now = str(pd.to_datetime('today'))                          #Getting the current date & time as a string
activity_df['Filename'] = cash_acct_num + ' ' +date_time_now + '.csv' #Concatenate it all as instructed

#STEP 9. DataFrame to hold all Bank Ref ID from Mapping file:
map_Bank_RefID = pd.DataFrame(mapping_df['Bank Ref ID'])

#STEP 10. DataFrame to hold all Bank Ref ID and Starting_Balance of Mapping file:
map_RefID_sartBalance = mapping_df[['Bank Ref ID', 'Starting_Balance']]

#STEP 11. For loop through each Bank Ref ID of STEP 9.:
for bankRefID in map_Bank_RefID['Bank Ref ID'].values:
    
    #STEP 12. Getting 'Starting_Balance' value from STEP 10.:
    temp_df = map_RefID_sartBalance[map_RefID_sartBalance['Bank Ref ID'] == bankRefID]
    start_balance_val = temp_df['Starting_Balance']
    
    #STEP 13. Output DataFrame with all columns of Bank Activity DataFrame where
    # 'Cash Account Number' equals 'Bank Ref ID':
    output_df = activity_df[activity_df['Cash Account Number'] == bankRefID]
    
    #STEP 14. MM DataFrame with all MM activity in Output DataFrame for current 
    # Bank Ref ID. MM activity can be identified if "STIF" exists in the 
    # 'Description column of the bank activity DataFrame:
    mm_df = output_df[output_df.Description.str.contains('STIF') == True]
    
    #STEP 15. Remove all MM activity found in STEP 14 from output DataFrame
    # by filtering out the index from the MM DataFrame:
    output_df = output_df.loc[~output_df.index.isin(mm_df.index)]
    
    #STEP 16. Create write_file DataFrame from Output DataFrame with all rows
    # from the following columns (which are last 7 columns of the DataFrame):
    #'Bank Reference ID','Post Date','Value Date','Amount','Description',
    #'Bank Account','Closing_Balance':
    cols = activity_df.columns[-8:-1]
    write_file = output_df.loc[:, cols]
    
    #STEP 17. Remove rows from write_file DataFrame if 'Bank Reference ID' is NA
    # by filtering out the rows with empty string:
    write_file = write_file[write_file['Bank Reference ID'] != '']
    
    #STEP 18. If write_file DataFrame is empty, print the 'Bank Reference ID' 
    # plus " has no activity"
    if write_file.empty:
        print(str(bankRefID) + ' has no activity')
        
    #STEP 19. Else, 


















