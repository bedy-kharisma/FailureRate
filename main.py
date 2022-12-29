import pandas as pd
import streamlit as st

#get sheet id
sheet_id='1yYY6kEVkBRRdmNcGG1cG2F3gbPA_OZJ5rUTWahx5X-U'
#convert google sheet to csv for easy handling
csv_url=(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
#create dataframe from csv
df=pd.read_csv(csv_url)
unq_mainsys=df['Main System'].unique()
df['Jumlah kegagalan']= df['Jumlah kegagalan'].astype(int)

st.markdown("# Failure Rate Calculator")
mainsys = st.selectbox('Pilih Main System apa yang akan Anda hitung',unq_mainsys)
#filter df based on main system selection single selectbox
filtered_df = df[df['Main System'] == mainsys]
#get unique project name based on filtered df
unq_proj=filtered_df['Project Name'].unique()
proj = st.multiselect('Data dari Project saja yang akan Anda gunakan',unq_proj,unq_proj)
#filter df based on multiple selection project name
filtered_df = filtered_df[filtered_df['Project Name'].isin(proj)]
#get unique vendor based on above filtered df
unq_vendor=filtered_df['Vendor Name'].unique()
vendor=st.multiselect('Data dari Vendor saja yang akan Anda gunakan',unq_vendor,unq_vendor)
#filter based on multiple select vendor name
filtered_df = filtered_df[filtered_df['Vendor Name'].isin(vendor)]

#sum unique values operating hours per year
#sum_unique_values = filtered_df.groupby('Operating Hours per Year')['Operating Hours per Year'].unique().sum()
#filtered_df['Total Operating Hours']=sum_unique_values.sum()
#filtered_df['Total Operating Hours']= filtered_df['Total Operating Hours'].astype(int)

# Create a new dataframe with the duplicates removed
df_no_duplicates = filtered_df.drop_duplicates(inplace=False)
# Group the data by the 'Product' column and sum the values in the 'Quantity' column
df_no_duplicates = df_no_duplicates.groupby('Project Name').sum()['Operating Hours per Year']
# Assign the sum back to the original dataframe
filtered_df['Operating Hours per Year'] = df_no_duplicates['Operating Hours per Year'].astype(int)

#calculate total quantity
filtered_df['Total Quantity'] = filtered_df.groupby('Item Name')['Quantity all Trainset'].transform('sum')
filtered_df['Total Quantity']= filtered_df['Total Quantity'].astype(int)

#calculate t = Total komponen*OH
filtered_df['Total komponen*OH']= filtered_df['Total Quantity']*filtered_df['Total Operating Hours']
filtered_df['Total komponen*OH']= filtered_df['Total komponen*OH'].astype(int)

# Define the function
def failure_rate(row):
    if row['Total Quantity'] == 0 or row['Total Operating Hours'] == 0:
        return 0
    if row['Jumlah kegagalan'] > 0:
        return row['Jumlah kegagalan'] / row['Total komponen*OH']
    else:
        return 1 / (row['Total Quantity'] * row['Total Operating Hours'])
# Apply the function to the dataframe
filtered_df['Failure Rate'] = filtered_df.apply(failure_rate, axis=1)
                               
#change into scientific format
def to_scientific(x):
    return '{:.2e}'.format(x)
filtered_df['Failure Rate'] = filtered_df['Failure Rate'].apply(to_scientific)

#show only unique item
unique_df = filtered_df.drop_duplicates(subset=['Item Ref', 'Item Name'])
unique_df  = unique_df .reset_index().drop(columns='index')
st.dataframe(unique_df[['Item Ref', 'Item Name','Total Operating Hours','Total Quantity','Jumlah kegagalan','Failure Rate']])


