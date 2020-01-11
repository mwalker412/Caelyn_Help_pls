# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 10:16:50 2020

@author: walkerm
"""

import pandas as pd
import plotly as plt
import plotly.graph_objects as go

#%% Get Data
path = r'C:\users\walkerm\desktop\Current_Aggregates.xlsx'
bucket_path = r'C:\users\walkerm\desktop\Current_Bucket.xlsx'


df = pd.read_excel(path)
#df.set_index(keys = ['Date','Service_Level'],inplace=True)
bucket_df = pd.read_excel(bucket_path)

standard_df = df[df['Service_Level'] == 'Standard']
shoprunner_df = df[df['Service_Level'] == 'Shop Runner']
overnight_df = df[df['Service_Level'] == 'Overnight']
twoday_df = df[df['Service_Level'] == 'Two Day']

#day_aggregated_df = df.groupby(level=0).mean()

df_list = [df,standard_df,shoprunner_df,overnight_df,twoday_df]


for _ in df_list:
    _.reset_index(inplace=True,drop=True)
    

#%% Need an easy win; graph 5-Day Promise defect

fiveday_df = pd.DataFrame()

fiveday_df['Date'] = standard_df['Date']
fiveday_df['DC'] = 1-standard_df['DC_Promise']
fiveday_df['BOSS'] = 1-standard_df['BOSS_Promise']
fiveday_df['Expectation'] = [.98 for i in range(len(fiveday_df))]
fiveday_df['Total_Units'] = standard_df['DC_Units'] + standard_df['BOSS_Units']
fiveday_df['Total_Defect_Units'] = standard_df['DC_Promise']*standard_df['DC_Units'] + standard_df['BOSS_Promise']*standard_df['BOSS_Units']
fiveday_df['Weighted_Average'] = 1-fiveday_df['Total_Defect_Units']/fiveday_df['Total_Units']

tempval = fiveday_df.Total_Units.max()
fiveday_df['Units_Rescale'] = fiveday_df.Total_Units/tempval



fiveday_df = fiveday_df[fiveday_df['Total_Units']>100].sort_values(by = ['Date'])


fig = go.Figure()

x0 = go.Scatter(name = 'DC 5-Day Promise',
                   x = fiveday_df['Date'],
                   y = fiveday_df['DC'],
                   mode = 'lines+markers',
                   )

x1 = go.Scatter(name = 'BOSS 5-Day Promise',
                x = fiveday_df['Date'],
                y = fiveday_df['BOSS'],
                mode = 'lines+markers',
                )

x2 = go.Scatter(name = 'Expectation',
                x = fiveday_df['Date'],
                y = fiveday_df['Expectation'],
                mode = 'lines')

x3 = go.Scatter(name = 'Weighted Average',
                x = fiveday_df['Date'],
                y = fiveday_df['Weighted_Average'],
                line = dict(width=2,dash='dash')
                )

x4 = go.Bar(name = '(Scaled) Volume',
            x = fiveday_df['Date'],
            y = fiveday_df['Units_Rescale'],
            opacity = 0.5,            
            )
    

fig.add_trace(x0)
fig.add_trace(x1)
fig.add_trace(x2)
fig.add_trace(x3)
fig.add_trace(x4)

#fig.update_xaxes(tickangle = 30)


fig.update_layout(
        title = 'Five Day Promise',
        annotations=[
                go.layout.Annotation(
                        text="via BigQuery",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0,
                        y=0)
    ])


'''
fig.update_layout(
    yaxis=dict(
        title="Rate",
        titlefont=dict(
            color="#1f77b4"
        ),
        tickfont=dict(
            color="#1f77b4"
        )
    ),
    yaxis2=dict(
        title="Volume",
        titlefont=dict(
            color="#ff7f0e"
        ),
        tickfont=dict(
            color="#ff7f0e"
        ),
        anchor="free",
        overlaying="y",
        side="left",
        position=0.15
        )
    )
'''
plt.offline.plot(fig,filename = r'C:\users\walkerm\desktop\overlaytest.html')

#%% Transit Time!

from plotly.subplots import make_subplots
transit_df = pd.DataFrame()
fig = make_subplots(rows = 2, cols = 2)


transit_df['Date'] = df.Date
transit_df['Type'] = df.Service_Level
transit_df['DC'] = 1-df.DC_Transit
transit_df['BOSS'] = 1-df.BOSS_Transit
transit_df['Expectation'] = [.98 for i in range(len(df))]
transit_df['Total_Units'] = df['DC_Units'] + df['BOSS_Units']
transit_df['Total_Defect_Units'] = df['DC_Transit']*df['DC_Units'] + df['BOSS_Transit']*df['BOSS_Units']
transit_df['Weighted_Average'] = 1-transit_df['Total_Defect_Units']/transit_df['Total_Units']


tempval = transit_df.Total_Units.max()
transit_df['Units_Rescale'] = transit_df.Total_Units/tempval


transit_df = transit_df[transit_df['Total_Units']>100].sort_values(by = ['Date'])

templist = ['Standard','Two Day','Shop Runner','Overnight']
trace_list = []

for x in range(4):
    tempfig = go.Figure()
    levelstr = templist[x]
    temptransit_df = transit_df[transit_df['Type'] == levelstr]

    
    x0 = go.Scatter(
        name = 'Transit via DC',
        x = temptransit_df['Date'],
        y = temptransit_df['DC'],
        legendgroup = 'group',
        mode = 'lines+markers')

    x1 = go.Scatter(name = 'BOSS',
                x = temptransit_df['Date'],
                y = temptransit_df['BOSS'],
                legendgroup = 'group',
                mode = 'lines+markers')

    x2 = go.Scatter(name = 'Expectation',
                x = temptransit_df['Date'],
                y = temptransit_df['Expectation'],
                legendgroup = 'group',
                mode = 'lines')

    x3 = go.Scatter(name = 'Weighted Average',
                x = temptransit_df['Date'],
                y = temptransit_df['Weighted_Average'],
                legendgroup = 'group',
                line = dict(color='firebrick', width=1,dash='dash')
                )

    x4 = go.Bar(name = '(Scaled) Volume',
            x = temptransit_df['Date'],
            y = temptransit_df['Units_Rescale'],
            legendgroup = 'group',
            opacity = 0.5,
            )
    
    temp_trace_list = [x0,x1,x2,x3,x4]
    
    row_calc = x%2+1
    
    col_calc = 1
    if x>1:
        col_calc += 1
        
    for _ in temp_trace_list:
        fig.add_trace(_, row = row_calc, col = col_calc)
        
    trace_list.append(tempfig)

#fig.add_trace(x0)
#fig.add_trace(x1)
#fig.add_trace(x2)
#fig.add_trace(x3)
#fig.add_trace(x4)
for x in range(1,5):    
    fig['layout'][f'xaxis{x}'].update(title=f'Transit Defect: {templist[x-1]}')

fig.update_layout(
        title = 'Transit Defect',
        showlegend=False
        )



plt.offline.plot(fig,filename = r'C:\users\walkerm\desktop\overlaytest1.html')

#%% Buckets!

bucket_list = ['DC','BOSS','DC_Transit','BOSS_Transit','DC_Promise','BOSS_Promise']

def df_slice(df,bucket_slice, standard_bool = False, dropna_bool = True, to_datetime_bool = True):
    '''pass bucket_slice as member of bucket_list'''
    
    ret_df = pd.DataFrame()
    if bucket_slice:
        ret_df['Date'] = df.Date
        ret_df['Service_Level'] = df.Service_Level
       
        for day in range(8):
            tempstr = f'{bucket_slice}_Day{day}'
            ret_df[tempstr] = df[tempstr]
            
    if standard_bool:
        ret_df = ret_df[ret_df['Service_Level'] == 'Standard']
        
    if dropna_bool:
        ret_df.dropna(inplace=True)
    
    if to_datetime_bool:
        ret_df['Date'] = pd.to_datetime(ret_df['Date'])
        
    return ret_df

#Probably going to put all of this into one DF; add additional arg to df_slice

def make_CDF(df, start_row = 2, end_row = df.shape[1]):
#    df.reset_index(inplace = True, drop = True)
    col_list = list(df.columns)
    ret_list = []
    
    for x in range(len(df)):
        temp_list = list(df.loc[x])
        iter_list = []
        
        for x in range(2): #don't forget the date and service_level boi
            iter_list.append(temp_list[x])
            
        temp_list = temp_list[start_row:end_row]
        
        iter_var = 0
    
        for x in range(len(temp_list)):
            iter_list.append(iter_var + temp_list[x])
            iter_var += temp_list[x]

        if not .99 < iter_var < 1.01:
            raise ValueError
        
        ret_list.append(iter_list)
        
    ret_df = pd.DataFrame(ret_list)
    ret_df.columns = col_list
    
    return ret_df


def hackish_join(df0, df1, join_column = 'Date', join_column2 = None, second_join = 'Service_Level', second_join2 = None,date_bool = True):
    '''Not fucking around any more'''
    # Going to load everything into a list. Return new df(list)
    
    if not join_column2:
        join_column2 = join_column
    if not second_join2:
        second_join2 = second_join
        
    if date_bool:
        df0[join_column] = pd.to_datetime(df0[join_column])
        df1[join_column2] = pd.to_datetime(df1[join_column2])
    
    
    df0 = df0.reset_index(drop = True).sort_values(by = [join_column,second_join])
    df1 = df1.reset_index(drop = True).sort_values(by = [join_column2,second_join2])
    
    tempdf = df1.drop(columns = [join_column2,second_join2])
    
    col_list = [*df0.columns,*tempdf.columns]
   
    master_list = [] # Append data by x&y value for loc
    
    for x in range(len(df0)):
        # Set value to search for
        search_combination = [df0.loc[x,join_column],df0.loc[x,second_join]]
        
        for y in range(len(df1)):
            ret_list = []
            search_iter = [df1.loc[y,join_column2],df1.loc[y,second_join2]]
            if search_combination == search_iter:
                ret_list = list(tempdf.loc[y])
                break
        
        if len(ret_list) == 0:
            pass
        else:
            temp_list = [*list(df0.loc[x]),*ret_list]
            master_list.append(temp_list)
    
    ret_df = pd.DataFrame(master_list)
    ret_df.columns = col_list
    return ret_df
        
    
        
        
        


DC_Bucket = df_slice(bucket_df,'DC')
BOSS_Bucket = df_slice(bucket_df,'BOSS')
DC_Transit_Bucket = df_slice(bucket_df, 'DC_Transit')
BOSS_Transit_Bucket = df_slice(bucket_df,'BOSS_Transit')
DC_Promise_Bucket = df_slice(bucket_df,'DC_Promise', True)
BOSS_Promise_Bucket = df_slice(bucket_df,'BOSS_Promise', True)


# TO_DO: Join with masterdf to get units! -> Weighted averages for weekly/monthly

# let's build out a test CDF bar graph for DC_Bucket

DC_Copy = df_slice(bucket_df,'DC_Promise', True)
DC_Copy = DC_Copy.groupby(['Service_Level'],as_index=False).mean()

#TypeError if to_datetime_bool is False
#DC_Copy = DC_Copy.groupby('Service_Level').resample('W-Mon',on='Index').mean().reset_index(inplace=True)


# Code goes here to calculate weighted averages


#// Don't forget to do this

fig = go.Figure()
fig = make_subplots(rows = 2, cols = 2)
trace_list = []

templist = ['Standard','Two Day','Shop Runner','Overnight']

temp_CDF = make_CDF(DC_Copy)


# TO_DO: make this not shit
for x in range(4):
    
    yvar = DC_Copy[DC_Copy['Service_Level'] == templist[x]].reset_index(drop=True)
    yvar = list(yvar.loc[0])
    yvar.remove(templist[x])
    
    
    trace0 = go.Bar(name = templist[x],
                x = [i for i in range(len(yvar))],
                y = yvar)
    
    
    yvar = temp_CDF[temp_CDF['Service_Level'] == templist[x]].reset_index(drop=True)
    yvar = list(yvar.loc[0])
    yvar.remove(templist[x])
    
    
    trace1 = go.Scatter(name = f'{templist[x]} CDF',
                        x = [i for i in range(len(yvar))],
                        y = yvar,
                        line = dict(color='firebrick', width=1,dash='dash'))
    
    temp_trace_list = [trace0,trace1]
    
    row_calc = x%2+1
    
    col_calc = 1
    if x>1:
        col_calc += 1
        
    for _ in temp_trace_list:
        fig.add_trace(_, row = row_calc, col = col_calc)

for x in range(1,5):    
    fig['layout'][f'xaxis{x}'].update(title=f'{templist[x-1]}')

fig.update_layout(
        title = 'DC Five Day Promise'
        )

        
plt.offline.plot(fig,filename = r'C:\users\walkerm\desktop\PDFCDF1.html')


        
#%% Sankey!

''' Need trailing week; write function to return a color based on percent change week over week 
'''

sankey_df = hackish_join(df,bucket_df)
sankey_df['DC_Total_Defect_Units'] = (sankey_df['DC_Defect'] + sankey_df['DC_Transit'] - sankey_df['DC_Double_Count']) * sankey_df['DC_Units']
sankey_df['BOSS_Total_Defect_Units'] = (sankey_df['BOSS_Defect'] + sankey_df['BOSS_Transit'] - sankey_df['BOSS_Double_Count']) * sankey_df['BOSS_Units']

#DC_Copy = DC_Copy.groupby('Service_Level').resample('W-Mon',on='Index').mean().reset_index(inplace=True)

sankey_df['Date'] = pd.to_datetime(sankey_df['Date'])

abs_sankey_df = pd.DataFrame()

paste_list = ['DC_Units','BOSS_Units','DC_Total_Defect_Units','BOSS_Total_Defect_Units']

#Build df of absolute values instead of rates
for x in sankey_df.columns:
    if x in paste_list:
        abs_sankey_df[x] = sankey_df[x]
    elif x[:2] == 'DC':
        abs_sankey_df[f'{x}_Sum'] = sankey_df[x] * sankey_df['DC_Units']
    elif x[:4] == 'BOSS':
        abs_sankey_df[f'{x}_Sum'] = sankey_df[x] * sankey_df['BOSS_Units']
    else:
        abs_sankey_df[x] = sankey_df[x]

standard_sankey_subdf = abs_sankey_df[abs_sankey_df['Service_Level'] == 'Standard']
exp_sankey_subdf = abs_sankey_df[abs_sankey_df['Service_Level'] != 'Standard']


master_date_agg = abs_sankey_df.resample('W-Sun',on = 'Date').sum().reset_index().sort_values(by = ['Date'],ascending=False)
standard_date_agg = standard_sankey_subdf.resample('W-Sun',on = 'Date').sum().reset_index().sort_values(by = ['Date'],ascending=False)
exp_date_agg = exp_sankey_subdf.resample('W-Sun',on = 'Date').sum().reset_index().sort_values(by = ['Date'],ascending=False)


value_list = master_date_agg.loc[0]
value_list_std = standard_date_agg.loc[0]
value_list_exp = exp_date_agg.loc[0]



#%% Temp cell for ctrl+enter

#might be the best way to do this:

# let's instead try a matrix, then transposing it
default_color = 'black'


help0 = value_list.DC_Units - value_list.DC_Defect_Sum
help1 = value_list.BOSS_Units - value_list.BOSS_Defect_Sum

standard_transit_defect = value_list_std.DC_Transit_Sum + value_list_std.BOSS_Transit_Sum
exp_transit_defect = value_list_exp.DC_Transit_Sum + value_list_exp.BOSS_Transit_Sum

error_bucket0 = 10
error_bucket1 = value_list.DC_Defect_Sum + value_list.BOSS_Defect_Sum

make_bucket0 = help0 + help1 - exp_transit_defect + standard_transit_defect

on_time_exp = value_list_exp.DC_Units + value_list_exp.BOSS_Units - value_list_exp.DC_Defect_Sum - value_list_exp.BOSS_Defect_Sum - value_list_exp.DC_Transit_Sum - value_list_exp.BOSS_Transit_Sum
on_time_std = value_list_std.DC_Units + value_list_std.BOSS_Units - value_list_std.DC_Defect_Sum - value_list_std.BOSS_Defect_Sum- value_list_std.DC_Transit_Sum - value_list_std.BOSS_Transit_Sum
#RESTART:
# Re-do these calculations. Might be helpful to do them outside of matrix framework and paste them in
'''
actually, it's best to draw this out on a piece of paper and hand write how to do all the calculations
'''
label_list= ['Root Node','2nd Root','Defect 0', 'Success1','Defect1','Perfect Shipments','Defect2','5 Day Compliance']

input_matrix = [[0,1,value_list.DC_Units,'Orders, DC-Fulfilled', default_color], #1; beginning of make bucket
                [0,1,value_list.BOSS_Units,'Orders, BOSS_Fulfilled',default_color],
                [0,2,10,'Failed/Cancelled orders (to be added)',default_color], #2; beginning of error bucket
                [1,3,help0,'DC - Sorted/Shipped on time', default_color], #3; continuation of make bucket
                [1,3,help1,'BOSS - Sorted/Shipped on time', default_color],
                [1,4,value_list.DC_Defect_Sum, 'DC - Not handled on time', default_color], #4; continuation of error bucket
                [1,4,value_list.BOSS_Defect_Sum, 'BOSS - Not handled on time',default_color],
                [2,4,10, 'Continuation of defect aggregation',default_color],
                [3,5,on_time_std, 'Standard packages delivered on time', default_color],        
                [3,5,on_time_exp, 'Expedited packages delivered on time',default_color], #5 IS PERFECT SHIPMENT BUCKET
                [3,6,standard_transit_defect, 'Standard packages delivered late',default_color],
                [3,6,exp_transit_defect, 'Expedited packages delivered late', default_color],
                [4,6,error_bucket1, 'Continuation of defect aggregation',default_color],
                [5,7,make_bucket0, 'Continuation of make aggregation',default_color],
                [6,7,value_list.DC_Double_Count_Sum + value_list.BOSS_Double_Count_Sum, 'Adjustment for double counted entries', default_color],
                [2,4,100,'Placeholder',default_color]
        ]


input_transpose = [[row[i] for row in input_matrix] for i in range(len(input_matrix[0]))]


fig = go.Figure(data = go.Sankey(
        node = dict(
                pad = 50,
                thickness = 20,
                line = dict(color = 'black',width = .5),
                color = 'darkslategray',
                label = label_list),
                
        
        link = dict(
                source = input_transpose[0],
                target = input_transpose[1],
                value = input_transpose[2],
                label = input_transpose[3],
                color = input_transpose[4]
                            
                )))

fig.update_layout(title_text = 'Test Sankey')
plt.offline.plot(fig, filename=r'C:\users\walkerm\desktop\sankey123123123.html')

#%%