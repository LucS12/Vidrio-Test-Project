#Necessary Packages:
import pandas as pd   #Needed to read in data into DataFrames & manipulate it
import datetime       #Used to get the current date and time

#STEP 3. Ask user for Bank Activity file location:
bank_activity_path = input("Provide the absolute path and filename of Bank Activity file: ")

#STEP 4. File paths for Mapping and Bank Activity files:
mapping_path = '/Desktop/Test Project[3]/Mapping/Cash_Rec_Mapping.xlsx'    

#STEP 4. Read  Mapping file & Bank Activity file into DataFrames:    
mapping_df = pd.read_excel(mapping_path)                 #Mapping DataFrame
bank_activity_df = pd.read_excel(bank_activity_path)     #Bank Activity DataFrame

#STEP 5. Replacing any NaNs on Bank Activity DataFrame with blank strings "":
bank_activity_df.fillna("", inplace=True)

#STEP 6. Creating blank DataFrame to hold exceptions:
exceptions_df = pd.DataFrame()

#STEP 7. Boolean variable to track if there are exceptions (initially False):
exception_exists = False

#STEP 8. Adding Named Columns to Bank Activity DataFrame:
  #New 'Bank Reference ID' column equal to original 'Reference Number' column:
bank_activity_df['Bank Reference ID'] = bank_activity_df['Reference Number']  

  #New 'Post Date' column equal to original 'Cash Post Date' column (date format):
bank_activity_df['Post Date'] = pd.to_datetime(bank_activity_df['Cash Post Date'])    

  #New 'Value Date' column equal to original 'Cash Value Date' column (date format):
bank_activity_df['Value Date'] = pd.to_datetime(bank_activity_df['Cash Value Date'])      
 
  #New 'Amount' column equal to original 'Transaction Amount Local' column:
bank_activity_df['Amount'] = bank_activity_df['Transaction Amount Local']

  #New 'Description column equal to a combo of the original transaction 
  # description columns shown in the list below:
desc_cols = ['Transaction Description 1','Transaction Description 2', 
             'Transaction Description 3', 'Transaction Description 4',
             'Transaction Description 5', 'Transaction Description 6',
             'Detailed Transaction Type Name', 'Transaction Type']

  #Separate each description with a space for readability:
bank_activity_df['Description'] = bank_activity_df[desc_cols].T.agg(' '.join)

  #New 'Bank Account' column equal to original 'Cash Account Number' column:
bank_activity_df['Bank Account'] = bank_activity_df['Cash Account Number']

  #New 'Closing_Balance' column equal to original 'Closing Balance Local' column:
bank_activity_df['Closing_Balance'] = bank_activity_df['Closing Balance Local']

  #New 'Filename' column equal to original 'Cash Account Number' column plus the
  # current date and time plus '.csv' formatted as a string:
cash_acct_num = bank_activity_df['Cash Account Number'].apply(str)          #Turning int column into string
date_time_now = str(pd.to_datetime('today'))                                #Getting the current date & time as a string
bank_activity_df['Filename'] = cash_acct_num + ' ' + date_time_now + '.csv' #Concatenate it all as instructed

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
    output_df = bank_activity_df[bank_activity_df['Cash Account Number'] == bankRefID]
    
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
    cols = bank_activity_df.columns[-8:-1]
    write_file = output_df.loc[:, cols]
    
    #STEP 17. Remove rows from write_file DataFrame if 'Bank Reference ID' is NA
    # by filtering out the rows with empty string:
    write_file = write_file[write_file['Bank Reference ID'] != '']
    
    #STEP 18. If write_file DataFrame is empty, print the 'Bank Reference ID' 
    # plus " has no activity"
    if write_file.empty:
        print(str(bankRefID) + ' has no activity')
        
    #STEP 19. Else, get 'Closing_Balance' from Bank Activity DataFrame for given
    # Bank Reference ID
    else:
        temp_activity_df = bank_activity_df[bank_activity_df['Bank Account'] == bankRefID]  #Filter DF for current Bank Ref ID
        bank_closing_balance = temp_activity_df['Closing_Balance']                          
        
        #STEP 20. Calculate overnight MM investment from MM DataFrame by adding
        # the negative transaction amounts as they are going into an MM tonight.
        # Need to multiply by -1 to get the total absolute value:
        overnight_mm_invest = mm_df[mm_df.Amount < 0].Amount.sum() * -1
        
        #STEP 21. Add starting balance row to write_file DataFrame, populating
        # the columns accordingly
            #'Bank Reference ID' = "Starting Balance"
            #'Post Date' = '2020-01-01'
            #'Value Date' = '2020-01-01'
            #'Amount' = balance from step 12
            #'Description' = "Starting Balance"
            #'Bank Account' = the given Bank Reference ID 
            #'Closing_Balance' = 0
        add_row = ['Starting Balance', '2020-01-01', '2020-01-01', 
                   start_bal_var.iloc[0], 'Starting Balance', bankRefID, 0]
        write_file.loc[len(write_file)] = add_row
        
        #STEP 22. Calculate closing balance from write_file DataFrame by 
        # summing the 'Amount' column:
        calc_closing_balance = round(write_file.Amount.sum(), 2)
        
        #STEP 23. If calc_closing_balance does NOT equal the sum of 
        #overnight_mm_invest plus bank_closing_balance... 
        closeBalance_MM_sum = bank_closing_balance.iloc[0] + overnight_mm_invest
        
        if closeBalance_MM_sum != calc_closing_balance:
            
            # STEP 23 ...add to exception DataFrame with Bank Reference ID, 
            # bank_closing_balance + MM value, and cal_closing_balance. 
            # Also change boolean variable to True:
            add_cols = ['Bank Reference ID', 'Close Balance Plus MM',  #List of columns to add
                        'Calculated Closing Balance']
            
            #Setting respective values to columns named above:
            exceptions_df.loc[len(exceptions_df), add_cols] = bankRefID, closeBalance_MM_sum, calc_closing_balance
            exception_exists = True   #Setting boolean variable to True
            
        #STEP 24. Save write_file DF to Output subfolder as excel with file name
        # Bank Reference ID + current date and time + '.xlsx' and 'Bank Transactions' tab:
        output_path = '/Desktop/Test Project[3]/Output/'
        out_filename = str(bankRefID) + date_time_now + '.xlsx'
        
        write_file.to_excel(output_path+out_filename,          #To excel file, no index column
                            sheet_name = 'Bank Transactions',
                            index = False)
        
        #STEP 25. Update mapping DataFrame with calc_closing_balance (STEP 22)
        # for the relevant Bank Reference ID:
        row_location = mapping_df.index[mapping_df['Bank Ref ID'] == bankRefID]  #Get row index of Bank Ref ID location
        mapping_df.loc[row_location, 'Starting_Balance'] = calc_closing_balance  #Update the value with STEP 22 variable
        
    #STEP 26. Save mapping DataFrame to excel, replacing existing file
    # Using variable from STEP 4 for the path and filename:
    mapping_df.to_excel(mapping_path, index=False)
    
    #STEP 27. If there are exceptions...
    if exception_exists:
        
        # STEP 27 ...place exception DataFrame to excel in Output subfolder.
        # use output path of STEP 24 to access subfolder:
        exceptions_df.to_excel(output_path+'exceptions.xlsx', index=False)
