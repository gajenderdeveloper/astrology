from django.shortcuts import render
from tradingview.function import * 
import pandas as pd 
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from .models import SectorSymbol


# Create your views here.
def dashboard(request):

    return render(request, 'tradingview/dashboard.html', {
                
    })


def option_chain(request):
    data = topGainer()
    df_sector = pd.DataFrame()
    df_sector = pd.DataFrame.from_records(SectorSymbol.objects.select_related("sector").only('symbol', 'sector__name').values('symbol', 'sector__name'))
    # replace Nifty with "Nifty 50"
    print("df_sector==============================99999999999")
    print(df_sector)

    top_gainers = data['top_gainers']
    #join top_gainers with df_sector on symbol
    top_gainers = top_gainers.merge(df_sector, on='symbol', how='left')
    print("top gainer==============================399999999999")

    print(top_gainers)
    df_metal = top_gainers[top_gainers['sector__name'] == 'NIFTY METAL'].sort_values(by='change_in_price_percentage', ascending=False)
    print("sector_metal==============================metal sector top gainers")
    print(df_metal)

    default_symbol = top_gainers['symbol'].iloc[0]

    data_call_db = MostActiveSymbol.objects.filter(type='CALL').values().order_by('-updated_at')
    data_call_db = pd.DataFrame.from_records(data_call_db)
    #print("data_call_db==================",data_call_db)

    data_call = pd.DataFrame(['HAL','ICICBANK','HDFCBANK','LT'], columns=["symbol"])
    most_active_contracts = render_to_string('tradingview/ajax_most_active_contracts.html', 
                                    {
                                        'df_call': data_call_db,
                                        #'df_put': data_put,
                                        'index':'calls-stocks-vol'
                                    }, 
                                    request=request)
    context = {
        'top_gainers':top_gainers,
        'default_symbol' : default_symbol,
        'most_active_contracts':most_active_contracts,
        'df_metal' : df_metal,
        'df_auto' : top_gainers[top_gainers['sector__name'] == 'NIFTY AUTO'].sort_values(by='change_in_price_percentage', ascending=False)  ,
        'df_bank' : top_gainers[top_gainers['sector__name'] == 'NIFTY BANK'].sort_values(by='change_in_price_percentage', ascending=False),
        'df_it' : top_gainers[top_gainers['sector__name'] == 'NIFTY IT'].sort_values(by='change_in_price_percentage', ascending=False),
        'df_pharma' : top_gainers[top_gainers['sector__name'] == 'NIFTY PHARMA'].sort_values(by='change_in_price_percentage', ascending=False)               
    }
    # check request is ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("AJAX request received from option_chain=")
        html_content = render_to_string('tradingview/ajax_top_gainner.html', context, request=request)
        #return HttpResponse(html_content)
        return JsonResponse({'html_content': html_content})
       
    return render(request, 'tradingview/option_chain.html', context)

def sectors(request):
    data = topGainer()
    top_gainers = data['top_gainers']
    print("top gainer sectors==============================99999999999")
    print(top_gainers)
    default_symbol = top_gainers['symbol'].iloc[0]

    data_call_db = MostActiveSymbol.objects.filter(type='CALL').values().order_by('-updated_at')
    data_call_db = pd.DataFrame.from_records(data_call_db)
    #print("data_call_db==================",data_call_db)

    #data_call = pd.DataFrame(['HAL','ICICBANK','HDFCBANK','LT'], columns=["symbol"])
    most_active_contracts = render_to_string('tradingview/ajax_most_active_contracts.html', 
                                    {
                                        'df_call': data_call_db,
                                        #'df_put': data_put,
                                        'index':'calls-stocks-vol'
                                    }, 
                                    request=request)
    context = {
        'top_gainers':top_gainers,
        'default_symbol' : default_symbol,
        'most_active_contracts':most_active_contracts
                
    }
    # check request is ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("AJAX request received from option_chain=")
        html_content = render_to_string('tradingview/ajax_top_gainner.html', context, request=request)
        #return HttpResponse(html_content)
        return JsonResponse({'html_content': html_content})
       
    return render(request, 'tradingview/option_chain.html', context)



def ajax_option_chain(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("AJAX request received from ajax_chart=================================") 
        try:
            symbol = request.GET.get('symbol')
            request_params = request.GET.dict()
            data = generate_stock_chart(request_params)
            df_oi = data['df_oi']
            today = data['today']
            print("AJAX response data:========================ajax_chart===============22")
            print(df_oi)

            time_grouped = data['time_grouped']
            fig = go.Figure()
            # Add line for call COI
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['call_coi'],
                name='Call COI',
                line=dict(color='green', width=2),
                mode='lines+markers'  # You can change this to just 'lines' if you prefer no markers
            ))

            # Add line for put COI 
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['put_coi'],
                name='Put COI',
                line=dict(color='red', width=2),
                mode='lines+markers'  # You can change this to just 'lines' if you prefer no markers
            ))

            # Add line for current price (assuming you have a 'current_price' column)
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['current_price'],  # Replace with your actual column name
                name='Price',
                line=dict(color='blue', width=2),
                mode='lines+markers',
                yaxis='y2'  # Use secondary y-axis for price
            ))
            title = '<b>' + symbol + ':</b> Call vs Put COI and Current Price by Time'
            title += f' (Date: {today})'
            fig.update_layout(
                height=600,

                title= title ,
                xaxis_title='Time',
                yaxis_title='Change in Open Interest',
                yaxis2=dict(
                    title='Price',
                    # titlefont=dict(color='blue'),
                    tickfont=dict(color='blue'),
                    overlaying='y',
                    side='right'
                ),
                showlegend=True,
                
            )
            chart_html = fig.to_html(full_html=True)
            last_price = df_oi['current_price'].values[0]
            context = {
                'df_oi': df_oi,
                'current_price' : last_price,
                'today': today,
                'symbol':symbol
            }
            html_content = render_to_string('tradingview/ajax_coi_data.html', context, request=request)
            #return HttpResponse(html_content)
            return JsonResponse({'chart_html': chart_html,'html_content': html_content})
        except Exception as e:
            print(f"Error in AJAX handler: {e}")
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method or not an AJAX request.'})
    

