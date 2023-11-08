import pandas as pd
from datetime import datetime
from dash import dash_table
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output  # Import the necessary classes
import plotly.express as px
import plotly.graph_objects as go  # Import go from plotly.graph_objects
import seaborn as sns

customer_purchase = pd.read_csv('https://github.com/nourhan-waleeed/Elrehab_data/raw/main/customer_purchase.zip')
points_trans = pd.read_csv('https://github.com/nourhan-waleeed/Elrehab_data/raw/main/points_trans.zip')
complaints = pd.read_csv('https://github.com/nourhan-waleeed/Elrehab_data/raw/main/complaints.zip')
complaints_info = pd.read_csv('https://github.com/nourhan-waleeed/Elrehab_data/raw/main/complaints_info.zip')


left_customers = complaints_info[complaints_info['complaint_in_days']<= complaints_info['recency_in_days']]
left_customers = left_customers[left_customers['complaint_count']>1]

customer_purchase['duration'] = customer_purchase['tenure']- customer_purchase['recency_in_days']

one_visit_data = customer_purchase[customer_purchase['segments'] == 'One Visit']
monthly_purchases = one_visit_data.groupby('الشهر ')['segments'].count().reset_index()

dep = complaints.groupby(['Department','reason']).size().reset_index(name='count')
seg = customer_purchase.groupby('segments').size().reset_index(name='count')

sales = customer_purchase.groupby(['الشهر ','القسم السلعي'])['المشتريات'].sum().reset_index()

daily_payments = points_trans.groupby('اسم اليوم')['قيمه المشتريات'].sum().reset_index()
monthly_payments = points_trans.groupby('الشهر')['قيمه المشتريات'].sum().reset_index()
seasonality_payments = points_trans.groupby('فصول')['قيمه المشتريات'].sum().reset_index()

unique_segments = customer_purchase.groupby("رقم العميل")["segments"].unique().reset_index()
segment_counts = unique_segments['segments'].value_counts().reset_index()
segment_counts = segment_counts.rename(columns={'segments': 'Segment', 'index': 'count'})

category_dropdown_options = [{'label': customer_purchase, 'value': customer_purchase} for customer_purchase in customer_purchase['القسم السلعي'].unique()]
segments_dropdown_options = [{'label': segment, 'value': segment} for segment in seg['segments'].unique()]
comp_dropdown_options = [{'label': department, 'value': department} for department in dep['Department'].unique()]

merged_other = customer_purchase[customer_purchase['segments'].isin(['Champion', 'Need Attention','One Visit'])]
merged_loyal = customer_purchase[customer_purchase['segments']=='Loyal']
other_counts = merged_other.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')
loyal_counts = merged_loyal.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')

category_sum = customer_purchase.groupby('القسم السلعي')['المشتريات'].sum().reset_index()
category_count = customer_purchase.groupby('القسم السلعي')['المشتريات'].count().reset_index()
category_sum=category_sum.rename(columns={'المشتريات': 'قيمة المشتريات'})
category_count=category_count.rename(columns={'المشتريات': 'عدد المنتجات'})
category_merge=pd.merge(category_sum, category_count, on='القسم السلعي', how='inner')

no_visits= points_trans.groupby('عدد الزيارات')['رقم العميل'].count().reset_index()

no_methods= complaints.groupby('Method of solution')['Ticket No'].count().reset_index()
no_source= complaints.groupby('Source')['Ticket No'].count().reset_index()

#comp
#comp_bar = comp.groupby([]'leave').size().reset_index(name='count')
comp_bar = complaints_info.groupby('segments')['Ticket No'].count().reset_index()

customer_reason_counts = left_customers.groupby(['Ticket No', 'reason']).size().reset_index(name='count')


c= complaints_info[['Ticket No','segments','leave_or_stay']]


complaints_info['complaint date'] = pd.to_datetime(complaints_info['complaint date']).dt.date
complaints_info['complaint date'] = complaints_info['complaint date'].apply(lambda x: x.strftime('%Y-%m-%d'))
date = complaints_info.groupby('complaint date').size().reset_index(name='count')

c = c.drop_duplicates()
c =c.groupby('leave_or_stay')[['Ticket No']].count().reset_index()

customer_counts = complaints_info['Ticket No'].value_counts()

repeated_customers = customer_counts[customer_counts > 1].index

repeated_customer_records = complaints_info[complaints_info['Ticket No'].isin(repeated_customers)]

# 8 of the 99 didn't come after the complaints
a = repeated_customer_records[repeated_customer_records['complaint_in_days']<= repeated_customer_records['recency_in_days']]
a['Ticket No'].nunique()

a = a[['Customoer ID','Department','reason','Satisfaction','Visits_No','segments','complaint_count','complaint_in_days','recency_in_days']]
a





fig = go.Figure()


app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'padding': '20px', 'background-color': '', 'text-align': 'right','color':'purple','font-size':'20px'}, children=[
    html.H1(children='فتح الله فرع الرحاب', style={'color': '#333', 'font-weight': 'bold','text-align': 'center','color':'purple','font-size':'50px'}),
    html.Hr(style={'border-top': '2px solid #999'}),
    dcc.RadioItems(
        options=[
            {'label': 'نسبة المبيعات على مدار فصول السنة', 'value': 'season'},
            {'label': 'نسبة المبيعات على مدار الاسبوع', 'value': 'days'},
            {'label': 'نسبة المبيعات على مدار الشهر', 'value': 'month'},
            {'label': 'عدد الزيارات ', 'value': 'freq'},
            {'label': 'معدل الشراء', 'value': 'معدل'}

        ],
        value='month',
        id='controls-and-radio-item',
        labelStyle={'display': 'block', 'margin-bottom': '10px', 'font-weight': 'bold', 'color': '#353'}
     ),
    
    
  html.Div([
          dcc.Graph(figure={}, id='controls-and-graph'),
      
       
            dcc.Graph(figure = px.bar(
            monthly_purchases,
            y='segments', x='الشهر ',
            color_discrete_sequence=px.colors.sequential.Viridis).
            update_layout(title='"One Visit" Segment by Month')),
            ], style={'display': 'flex', 'flex-direction': 'row'}),
    
           

      
   html.Div([
       
       dcc.Graph(figure= px.scatter(
           customer_purchase,
           x='recency_in_days',
           y='tenure',
           color='segments',
           labels={
                     "recency_in_days":'اخر يوم اشترى فيه',
                     "tenure": "عدد الايام من اول زياره  "
                 },
           color_discrete_sequence=px.colors.sequential.Viridis
            ).update_layout(title='relation between recency & number of days')),

   ]),
    
    
    
    
        html.Div([
            dcc.Dropdown(
        id='segment-dropdown',
        options=segments_dropdown_options,
        multi=True,  # Allow for selecting multiple segments
        value=customer_purchase['segments'].unique(),  # Default to all segments
        placeholder="Select segment(s)"
    ),
            
        dcc.Graph(id='segment-plot'),
  
            
        ]),
        dash_table.DataTable(
        id='segment-table',
        columns=[
            {'name': 'رقم العميل', 'id': 'رقم العميل'},
            {'name': 'عدد الزيارات', 'id': 'عدد الزيارات'},
            {'name': 'معدل الشراء', 'id': 'معدل الشراء'},
        ],
        data=[]
    ),
    
        
        html.Div([
            dcc.Dropdown(
        id='category-dropdown',
        options=category_dropdown_options,
        multi=True,  # Allow for selecting multiple segments
        value=customer_purchase['القسم السلعي'].unique(),  # Default to all segments
        placeholder="Select Category"
    ),
    
        ]),
    
    html.Div([
        
           dcc.Graph(id='cat-plot1'),
          dcc.Graph(id='cat-plot2')],
        style={'display': 'flex', 'flex-direction': 'row'}),
    
   html.Div([
        
           dcc.Graph(id='cat-plot3'),
          dcc.Graph(id='cat-plot4')],
        style={'display': 'flex', 'flex-direction': 'row'}),        
    
            

        
    

        html.Div([

     dcc.Graph(
    figure = px.scatter(customer_purchase, x='duration', y='عدد الزيارات', title='Scatter Plot of Duration vs. عدد الزيارات',size='معدل الشراء',color_discrete_sequence=px.colors.sequential.Viridis
).update_layout(
    xaxis_title='Duration',
    yaxis_title='عدد الزيارات',
    showlegend=False  
    ))

    ]),
    
    html.Div([
            html.Hr(style={'border-top': '3px solid #999'}),
            html.H1(children='شكاوي فرع الرحاب', style={'color': '#333', 'font-weight': 'bold','text-align': 'center','color':'purple','font-size':'30px'}),       
    ]),
    
    
            html.Div([
            dcc.Dropdown(
        id='comp-dropdown',
        options=comp_dropdown_options,
        multi=True,  # Allow for selecting multiple segments
        value=dep['Department'].unique(),  # Default to all segments
        placeholder="Select department(s)"
    ),
            
        dcc.Graph(id='comp-plot'),
  
            
        ]),
    
    
    html.Div([
        dcc.RadioItems(
        options=[
            {'label': 'طريقة استقبال الشكاوي', 'value': 'Source'},
            {'label': 'طريقة حل الشكاوي', 'value': 'Method Of Solution'}

        ],
        value='Source',
        id='comp-big-radio-item',
        labelStyle={'display': 'block', 'margin-bottom': '17px', 'font-weight': 'bold', 'color': '#353','font-size':'25px'})
    
    
    ]),
    
    
    
    
    html.Div([
    
         dcc.Graph(figure={}, id='source-sol-plot'),
    
    
            
        dcc.Graph(figure=px.bar(
            c,
            x='leave_or_stay',
            y='Ticket No',
            #color='segments',
                color_discrete_sequence=px.colors.sequential.Viridis,
    title='نسبة المغادرة بمعدل الشكاوي',
    labels={'segments': 'Stay=0 Leave=1'},
        ).update_layout(
    xaxis_title='Ticket No',
    showlegend=False
    ))], style={'display': 'flex', 'flex-direction': 'row'}),  

    
    
   html.Div([
       dcc.Graph(figure=px.line(
       date,
       x='complaint date',
       y='count',
        title='Complaints Over Time',
        labels={'complaint_date': 'Date', 'count': 'Complaint Count'}
        ))]),  

        

 
            html.Div([
    dash_table.DataTable(
        data=customer_reason_counts.to_dict('records'),
        columns=[{"name": i, "id": i} for i in customer_reason_counts.columns],
        sort_action='native',
        sort_mode='single',
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
        style_data_conditional=[
            {
                'if': {'filter_query': '{Ticket No} = 608494.0'},
                'backgroundColor': 'red'  # You can assign a unique color for each customer ID here
            },
            {
                'if': {'filter_query': '{Ticket No} = 2'},
                'backgroundColor': 'blue'
            },

    
    
])            
]),   
    
    
html.Div([
    dash_table.DataTable(
        data=a.to_dict('records'),
        columns=[{"name": i, "id": i} for i in a.columns],
        sort_action='native',
        sort_mode='single',
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
        sort_by=[{'column_id': 'complaint_count', 'direction': 'desc'}]
    ), 
  
]),  

    
    
])
@app.callback(
    Output(component_id='source-sol-plot', component_property='figure'),
    Input(component_id='comp-big-radio-item', component_property='value')
)



def update_graph_source_sol(chosen_option):
    if chosen_option == 'Method Of Solution':
        figure = px.bar(
            no_methods,
            y='Method of solution',
            x='Ticket No',
            orientation = 'h',
          title='طريقة حل الشكاوي'
            ,color_discrete_sequence=px.colors.sequential.Viridis
        )
        
    else:
        figure = px.bar(
            no_source,
            x='Ticket No' ,
            y='Source',
            orientation = 'h',
            title='طريقة استقبال الشكاوي'
            ,color_discrete_sequence=px.colors.sequential.Viridis
        )



    return figure










@app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(chosen_option):
    if chosen_option == 'season':
        figure = px.bar(
            seasonality_payments,
            x='فصول',
            y='قيمه المشتريات',
            title='المبيعات على مدار فصول السنة'
            ,color_discrete_sequence=px.colors.sequential.Viridis
        )
    elif chosen_option == 'days':
        figure = px.bar(
            daily_payments,
            x='اسم اليوم',
            y='قيمه المشتريات',
            title='المبيعات على مدار الاسبوع'
            ,color_discrete_sequence=px.colors.sequential.Viridis
        )
    elif chosen_option == 'month':
        figure = px.line(
            monthly_payments,
            x='الشهر',
            y='قيمه المشتريات',
            title='المبيعات على مدار الشهر',
            color_discrete_sequence=px.colors.sequential.Viridis)
           #figure.update_layout(barmode='group', bargap=0.2)
            
    elif chosen_option == 'freq':

        figure = px.histogram(
            points_trans,
            x='عدد الزيارات',
            title='Box Plot of Frequency of Visits',
            color_discrete_sequence=px.colors.sequential.Viridis)


    elif chosen_option == 'معدل':

        figure = px.box(
            customer_purchase,
            x='معدل الشراء',
            title='Box Plot of Frequency of Visits',
            color_discrete_sequence=px.colors.sequential.Viridis)
        

    return figure






@app.callback(
    Output('segment-plot', 'figure'),
    Input('segment-dropdown', 'value')
)
def update_segment_plot(selected_segments):
    if selected_segments:
        filtered_data = seg[seg['segments'].isin(selected_segments)]

        fig = px.bar(
            filtered_data,
            x='segments',
            y='count',
            title='Number of Customers by Segment',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        return fig
    return {}

@app.callback(
    Output('segment-table', 'data'),
    Input('segment-dropdown', 'value')
)
def update_segment_table(selected_segments):
    if selected_segments:
        selected_data = customer_purchase[customer_purchase['segments'].isin(selected_segments)][['رقم العميل', 'عدد الزيارات', 'معدل الشراء']]
        unique_data = selected_data.drop_duplicates(subset=['رقم العميل'])
        sorted_data = unique_data.sort_values(by=['عدد الزيارات','معدل الشراء'], ascending=[False,False])

        return sorted_data.head(10).to_dict('records')
    return []



        
    

    



@app.callback(
    Output('comp-plot', 'figure'),
    Input('comp-dropdown', 'value')
)



def update_comp_plot(selected_comp):
    if selected_comp:
        filtered_data = dep[dep['Department'].isin(selected_comp)]
        
        fig = px.bar(
            filtered_data,
            x='reason',  
            y='count',
            title='Number of Customers by Subcategory',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        
        return fig
    return {}



    
    
    
    
    
    
    
    
@app.callback(
    [Output('cat-plot1', 'figure'),Output('cat-plot2', 'figure'),Output('cat-plot3', 'figure'),Output('cat-plot4', 'figure')],
    Input('category-dropdown', 'value')
)



def update_cat_plot(selected_cat):
    if selected_cat:
        
        other_counts = merged_other.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')
        loyal_counts = merged_loyal.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')
        
        
        
        filtered_data = loyal_counts[loyal_counts['القسم السلعي'].isin(selected_cat)]
        filtered_data2 = other_counts[other_counts['القسم السلعي'].isin(selected_cat)]
        filtered_data3 = sales[sales['القسم السلعي'].isin(selected_cat)]
        filtered_data4 = category_merge[category_merge['القسم السلعي'].isin(selected_cat)]

        figure1 = px.bar(
            filtered_data,
            y='count', x='segments',color='القسم السلعي',
            color_discrete_sequence=px.colors.sequential.Viridis,
            title='Most Selling Categories for Loyal Segment')
            
        figure2 = px.bar(
            filtered_data2,
            y='count', x='segments',color='القسم السلعي',
            color_discrete_sequence=px.colors.sequential.Viridis
            ,title='Most Selling Categories for Other Segments')
        
        figure3 = px.line(
            filtered_data3,
            x='الشهر ', y='المشتريات',color='القسم السلعي',
            color_discrete_sequence=px.colors.sequential.Viridis)
        
        
        figure4 = px.bar(
            filtered_data4,
            x='القسم السلعي',
            y=['عدد المنتجات', 'قيمة المشتريات'],
            barmode='group',
            labels={'value': 'Value'},
            title='Comparison of Product Count and Purchase Value by Category',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        
        
        

        
        return figure1, figure2, figure3, figure4
    return {}, {}, {}, {}

 

if __name__ == '__main__':
    app.run_server(debug=True, port=8805)