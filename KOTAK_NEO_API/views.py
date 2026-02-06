from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.contrib import messages
import json
import logging

from KOTAK_NEO_API.models import (
    KotakNeoUserToken, KotakNeoInstrument, KotakNeoOrder,
    KotakNeoMarketData, KotakNeoHolding, KotakNeoAlert,
    KotakNeoOptionChain, KotakNeoAPILog
)
from KOTAK_NEO_API.kotak_integration import KotakNeoAPI

logger = logging.getLogger(__name__)


# Dashboard Views

@login_required
def kotak_dashboard(request):
    """Main dashboard for Kotak Neo trading"""
    try:
        # Get user tokens
        user_tokens = KotakNeoUserToken.objects.filter(status='active')
        
        # Get recent orders
        recent_orders = KotakNeoOrder.objects.select_related('user_token', 'instrument').order_by('-created_at')[:10]
        
        # Get recent market data
        recent_market_data = KotakNeoMarketData.objects.select_related('instrument').order_by('-timestamp')[:20]
        
        # Get active alerts
        active_alerts = KotakNeoAlert.objects.select_related('user_token', 'instrument').filter(status='ACTIVE')[:10]
        
        # Get holdings summary
        holdings_summary = KotakNeoHolding.objects.select_related('instrument').aggregate(
            total_holdings=Count('id'),
            total_value=Sum('market_value'),
            total_pnl=Sum('pnl')
        )
        
        # Get API logs summary
        api_logs_summary = KotakNeoAPILog.objects.aggregate(
            total_calls=Count('id'),
            error_calls=Count('id', filter=Q(log_level='ERROR')),
            avg_response_time=Avg('response_time')
        )
        
        context = {
            'user_tokens': user_tokens,
            'recent_orders': recent_orders,
            'recent_market_data': recent_market_data,
            'active_alerts': active_alerts,
            'holdings_summary': holdings_summary,
            'api_logs_summary': api_logs_summary,
        }
        
        return render(request, 'KOTAK_NEO_API/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, 'KOTAK_NEO_API/dashboard.html', {})


@login_required
def kotak_orders_view(request):
    """View for managing orders"""
    try:
        # Get orders with pagination
        orders = KotakNeoOrder.objects.select_related('user_token', 'instrument').order_by('-created_at')
        
        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        user_filter = request.GET.get('user')
        if user_filter:
            orders = orders.filter(user_token__user_id=user_filter)
        
        # Pagination
        paginator = Paginator(orders, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get order statistics
        order_stats = KotakNeoOrder.objects.aggregate(
            total_orders=Count('id'),
            pending_orders=Count('id', filter=Q(status='PENDING')),
            completed_orders=Count('id', filter=Q(status='COMPLETE')),
            rejected_orders=Count('id', filter=Q(status='REJECTED'))
        )
        
        context = {
            'page_obj': page_obj,
            'order_stats': order_stats,
            'status_choices': KotakNeoOrder.ORDER_STATUS_CHOICES,
            'user_tokens': KotakNeoUserToken.objects.filter(status='active')
        }
        
        return render(request, 'KOTAK_NEO_API/orders.html', context)
        
    except Exception as e:
        logger.error(f"Orders view error: {str(e)}")
        messages.error(request, f"Error loading orders: {str(e)}")
        return render(request, 'KOTAK_NEO_API/orders.html', {})


@login_required
def kotak_holdings_view(request):
    """View for managing holdings"""
    try:
        # Get holdings with pagination
        holdings = KotakNeoHolding.objects.select_related('user_token', 'instrument').order_by('-updated_at')
        
        # Apply filters
        user_filter = request.GET.get('user')
        if user_filter:
            holdings = holdings.filter(user_token__user_id=user_filter)
        
        # Pagination
        paginator = Paginator(holdings, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get holdings summary
        holdings_summary = KotakNeoHolding.objects.aggregate(
            total_holdings=Count('id'),
            total_value=Sum('market_value'),
            total_pnl=Sum('pnl'),
            avg_pnl_percentage=Avg('pnl_percentage')
        )
        
        context = {
            'page_obj': page_obj,
            'holdings_summary': holdings_summary,
            'user_tokens': KotakNeoUserToken.objects.filter(status='active')
        }
        
        return render(request, 'KOTAK_NEO_API/holdings.html', context)
        
    except Exception as e:
        logger.error(f"Holdings view error: {str(e)}")
        messages.error(request, f"Error loading holdings: {str(e)}")
        return render(request, 'KOTAK_NEO_API/holdings.html', {})


@login_required
def kotak_market_data_view(request):
    """View for market data"""
    try:
        # Get market data with pagination
        market_data = KotakNeoMarketData.objects.select_related('instrument').order_by('-timestamp')
        
        # Apply filters
        instrument_filter = request.GET.get('instrument')
        if instrument_filter:
            market_data = market_data.filter(instrument__tradingsymbol__icontains=instrument_filter)
        
        exchange_filter = request.GET.get('exchange')
        if exchange_filter:
            market_data = market_data.filter(instrument__exchange=exchange_filter)
        
        # Pagination
        paginator = Paginator(market_data, 100)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'exchanges': KotakNeoInstrument.objects.values_list('exchange', flat=True).distinct()
        }
        
        return render(request, 'KOTAK_NEO_API/market_data.html', context)
        
    except Exception as e:
        logger.error(f"Market data view error: {str(e)}")
        messages.error(request, f"Error loading market data: {str(e)}")
        return render(request, 'KOTAK_NEO_API/market_data.html', {})


@login_required
def kotak_alerts_view(request):
    """View for managing alerts"""
    try:
        # Get alerts with pagination
        alerts = KotakNeoAlert.objects.select_related('user_token', 'instrument').order_by('-created_at')
        
        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter:
            alerts = alerts.filter(status=status_filter)
        
        alert_type_filter = request.GET.get('alert_type')
        if alert_type_filter:
            alerts = alerts.filter(alert_type=alert_type_filter)
        
        # Pagination
        paginator = Paginator(alerts, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status_choices': KotakNeoAlert.ALERT_STATUS_CHOICES,
            'alert_type_choices': KotakNeoAlert.ALERT_TYPE_CHOICES,
            'user_tokens': KotakNeoUserToken.objects.filter(status='active'),
            'instruments': KotakNeoInstrument.objects.filter(is_active=True)
        }
        
        return render(request, 'KOTAK_NEO_API/alerts.html', context)
        
    except Exception as e:
        logger.error(f"Alerts view error: {str(e)}")
        messages.error(request, f"Error loading alerts: {str(e)}")
        return render(request, 'KOTAK_NEO_API/alerts.html', {})


# API Views

@csrf_exempt
@require_http_methods(["POST"])
def kotak_api_place_order(request):
    """API endpoint to place order"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['tradingsymbol', 'transaction_type', 'quantity']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Initialize API
        api = KotakNeoAPI()
        
        # Place order
        order_response = api.place_order(
            tradingsymbol=data['tradingsymbol'],
            transaction_type=data['transaction_type'],
            quantity=data['quantity'],
            product=data.get('product', 'NRML'),
            order_type=data.get('order_type', 'LIMIT'),
            price=data.get('price'),
            trigger_price=data.get('trigger_price')
        )
        
        return JsonResponse({
            'success': True,
            'order_id': order_response.get('order_id'),
            'message': 'Order placed successfully'
        })
        
    except Exception as e:
        logger.error(f"Place order API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def kotak_api_get_quote(request):
    """API endpoint to get quote"""
    try:
        instruments = request.GET.getlist('instruments')
        
        if not instruments:
            return JsonResponse({'error': 'No instruments provided'}, status=400)
        
        # Initialize API
        api = KotakNeoAPI()
        
        # Get quotes
        quotes = api.get_quote(instruments)
        
        return JsonResponse({
            'success': True,
            'quotes': quotes
        })
        
    except Exception as e:
        logger.error(f"Get quote API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def kotak_api_get_holdings(request):
    """API endpoint to get holdings"""
    try:
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'User ID required'}, status=400)
        
        # Initialize API
        api = KotakNeoAPI(user_id=user_id)
        
        
        # Get holdings
        holdings = api.get_holdings()
        
        return JsonResponse({
            'success': True,
            'holdings': holdings
        })
        
    except Exception as e:
        logger.error(f"Get holdings API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def kotak_api_get_option_chain(request):
    """API endpoint to get option chain"""
    try:
        symbol = request.GET.get('symbol')
        expiry_date = request.GET.get('expiry_date')
        
        if not symbol:
            return JsonResponse({'error': 'Symbol required'}, status=400)
        
        # Initialize API
        api = KotakNeoAPI()
        
        # Get option chain
        option_chain = api.get_option_chain(symbol, expiry_date)
        
        return JsonResponse({
            'success': True,
            'option_chain': option_chain
        })
        
    except Exception as e:
        logger.error(f"Get option chain API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# Management Views

@staff_member_required
def kotak_token_management(request):
    """View for managing user tokens"""
    try:
        if request.method == 'POST':
            action = request.POST.get('action')
            user_id = request.POST.get('user_id')
            
            if action == 'create_token':
                # Create new token (this would typically require user authentication)
                messages.success(request, f"Token creation initiated for user {user_id}")
                
            elif action == 'refresh_token':
                # Refresh existing token
                try:
                    token = KotakNeoUserToken.objects.get(user_id=user_id)
                    api = KotakNeoAPI(user_id=user_id)
                    messages.success(request, f"Token refreshed for user {user_id}")
                except KotakNeoUserToken.DoesNotExist:
                    messages.error(request, f"Token not found for user {user_id}")
                    
            elif action == 'delete_token':
                # Delete token
                try:
                    token = KotakNeoUserToken.objects.get(user_id=user_id)
                    token.delete()
                    messages.success(request, f"Token deleted for user {user_id}")
                except KotakNeoUserToken.DoesNotExist:
                    messages.error(request, f"Token not found for user {user_id}")
        
        # Get all tokens
        tokens = KotakNeoUserToken.objects.all().order_by('-updated_at')
        
        context = {
            'tokens': tokens
        }
        
        return render(request, 'KOTAK_NEO_API/token_management.html', context)
        
    except Exception as e:
        logger.error(f"Token management error: {str(e)}")
        messages.error(request, f"Error in token management: {str(e)}")
        return render(request, 'KOTAK_NEO_API/token_management.html', {})


@staff_member_required
def kotak_api_logs_view(request):
    """View for API logs"""
    try:
        # Get API logs with pagination
        logs = KotakNeoAPILog.objects.select_related('user_token').order_by('-created_at')
        
        # Apply filters
        log_level_filter = request.GET.get('log_level')
        if log_level_filter:
            logs = logs.filter(log_level=log_level_filter)
        
        user_filter = request.GET.get('user')
        if user_filter:
            logs = logs.filter(user_token__user_id=user_filter)
        
        # Pagination
        paginator = Paginator(logs, 100)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get log statistics
        log_stats = KotakNeoAPILog.objects.aggregate(
            total_logs=Count('id'),
            error_logs=Count('id', filter=Q(log_level='ERROR')),
            warning_logs=Count('id', filter=Q(log_level='WARNING')),
            avg_response_time=Avg('response_time')
        )
        
        context = {
            'page_obj': page_obj,
            'log_stats': log_stats,
            'log_level_choices': KotakNeoAPILog.LOG_LEVEL_CHOICES,
            'user_tokens': KotakNeoUserToken.objects.all()
        }
        
        return render(request, 'KOTAK_NEO_API/api_logs.html', context)
        
    except Exception as e:
        logger.error(f"API logs view error: {str(e)}")
        messages.error(request, f"Error loading API logs: {str(e)}")
        return render(request, 'KOTAK_NEO_API/api_logs.html', {})


# Sync Views

@staff_member_required
def kotak_sync_holdings(request):
    """Manual sync holdings"""
    try:
        from .kotak_neo_cron import sync_kotak_holdings
        
        sync_kotak_holdings()
        messages.success(request, "Holdings sync completed successfully")
        
    except Exception as e:
        logger.error(f"Manual holdings sync error: {str(e)}")
        messages.error(request, f"Holdings sync failed: {str(e)}")
    
    return redirect('kotak_dashboard')


@staff_member_required
def kotak_sync_market_data(request):
    """Manual sync market data"""
    try:
        from .kotak_neo_cron import sync_kotak_market_data
        
        sync_kotak_market_data()
        messages.success(request, "Market data sync completed successfully")
        
    except Exception as e:
        logger.error(f"Manual market data sync error: {str(e)}")
        messages.error(request, f"Market data sync failed: {str(e)}")
    
    return redirect('kotak_dashboard')


@staff_member_required
def kotak_sync_instruments(request):
    """Manual sync instruments"""
    try:
        from .kotak_neo_cron import sync_kotak_instruments
        
        sync_kotak_instruments()
        messages.success(request, "Instruments sync completed successfully")
        
    except Exception as e:
        logger.error(f"Manual instruments sync error: {str(e)}")
        messages.error(request, f"Instruments sync failed: {str(e)}")
    
    return redirect('kotak_dashboard')


# Alert Management Views

@login_required
def kotak_create_alert(request):
    """Create new alert"""
    try:
        if request.method == 'POST':
            # Get form data
            name = request.POST.get('name')
            user_token_id = request.POST.get('user_token')
            instrument_id = request.POST.get('instrument')
            alert_type = request.POST.get('alert_type')
            condition = request.POST.get('condition')
            target_value = request.POST.get('target_value')
            is_repeatable = request.POST.get('is_repeatable') == 'on'
            description = request.POST.get('description')
            
            # Validate required fields
            if not all([name, user_token_id, instrument_id, alert_type, condition, target_value]):
                messages.error(request, "All required fields must be filled")
                return redirect('kotak_alerts_view')
            
            # Create alert
            alert = KotakNeoAlert.objects.create(
                name=name,
                user_token_id=user_token_id,
                instrument_id=instrument_id,
                alert_type=alert_type,
                condition=condition,
                target_value=target_value,
                is_repeatable=is_repeatable,
                description=description
            )
            
            messages.success(request, f"Alert '{name}' created successfully")
            return redirect('kotak_alerts_view')
        
        # Get form data
        context = {
            'user_tokens': KotakNeoUserToken.objects.filter(status='active'),
            'instruments': KotakNeoInstrument.objects.filter(is_active=True),
            'alert_type_choices': KotakNeoAlert.ALERT_TYPE_CHOICES,
            'condition_choices': KotakNeoAlert.CONDITION_CHOICES
        }
        
        return render(request, 'KOTAK_NEO_API/create_alert.html', context)
        
    except Exception as e:
        logger.error(f"Create alert error: {str(e)}")
        messages.error(request, f"Error creating alert: {str(e)}")
        return redirect('kotak_alerts_view')


@login_required
def kotak_edit_alert(request, alert_id):
    """Edit existing alert"""
    try:
        alert = get_object_or_404(KotakNeoAlert, id=alert_id)
        
        if request.method == 'POST':
            # Update alert
            alert.name = request.POST.get('name')
            alert.user_token_id = request.POST.get('user_token')
            alert.instrument_id = request.POST.get('instrument')
            alert.alert_type = request.POST.get('alert_type')
            alert.condition = request.POST.get('condition')
            alert.target_value = request.POST.get('target_value')
            alert.is_repeatable = request.POST.get('is_repeatable') == 'on'
            alert.description = request.POST.get('description')
            alert.save()
            
            messages.success(request, f"Alert '{alert.name}' updated successfully")
            return redirect('kotak_alerts_view')
        
        context = {
            'alert': alert,
            'user_tokens': KotakNeoUserToken.objects.filter(status='active'),
            'instruments': KotakNeoInstrument.objects.filter(is_active=True),
            'alert_type_choices': KotakNeoAlert.ALERT_TYPE_CHOICES,
            'condition_choices': KotakNeoAlert.CONDITION_CHOICES
        }
        
        return render(request, 'KOTAK_NEO_API/edit_alert.html', context)
        
    except Exception as e:
        logger.error(f"Edit alert error: {str(e)}")
        messages.error(request, f"Error editing alert: {str(e)}")
        return redirect('kotak_alerts_view')


@login_required
def kotak_delete_alert(request, alert_id):
    """Delete alert"""
    try:
        alert = get_object_or_404(KotakNeoAlert, id=alert_id)
        alert_name = alert.name
        alert.delete()
        
        messages.success(request, f"Alert '{alert_name}' deleted successfully")
        
    except Exception as e:
        logger.error(f"Delete alert error: {str(e)}")
        messages.error(request, f"Error deleting alert: {str(e)}")
    
    return redirect('kotak_alerts_view')


# Utility Views

@login_required
def kotak_market_status(request):
    """Get market status"""
    try:
        api = KotakNeoAPI()
        market_status = api.get_market_status()
        
        return JsonResponse({
            'success': True,
            'market_status': market_status
        })
        
    except Exception as e:
        logger.error(f"Market status error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def kotak_instrument_search(request):
    """Search instruments"""
    try:
        query = request.GET.get('q', '')
        
        if not query:
            return JsonResponse({'instruments': []})
        
        instruments = KotakNeoInstrument.objects.filter(
            Q(tradingsymbol__icontains=query) | 
            Q(name__icontains=query)
        ).filter(is_active=True)[:20]
        
        results = []
        for instrument in instruments:
            results.append({
                'id': instrument.id,
                'tradingsymbol': instrument.tradingsymbol,
                'name': instrument.name,
                'exchange': instrument.exchange,
                'instrument_type': instrument.instrument_type
            })
        
        return JsonResponse({'instruments': results})
        
    except Exception as e:
        logger.error(f"Instrument search error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
