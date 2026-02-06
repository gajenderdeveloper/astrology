# Kotak Neo API Integration

This Django app provides a comprehensive integration with the Kotak Neo trading API, featuring auto-authentication, user token management, admin model views, and automated cron jobs.

## Features

### 🔐 Auto-Authentication
- Automatic token management and refresh
- Secure storage of access and refresh tokens
- Token expiration handling
- Multiple user support

### 📊 Admin Model Views
- Comprehensive Django admin interface
- Real-time data monitoring
- Order management
- Holdings tracking
- Alert management
- API logs and debugging

### ⏰ Automated Cron Jobs
- Market data synchronization (every 5 minutes during market hours)
- Holdings synchronization (every 30 minutes during market hours)
- Alert monitoring (every 2 minutes during market hours)
- Option chain synchronization (every 15 minutes during market hours)
- Token management (hourly)
- Data cleanup (daily)

### 🎯 Trading Features
- Order placement and management
- Real-time market data
- Portfolio holdings tracking
- Option chain data
- Custom alerts and notifications

## Models

### KotakNeoUserToken
Stores user authentication tokens with auto-refresh capabilities.

### KotakNeoInstrument
Manages trading instruments with detailed metadata.

### KotakNeoOrder
Tracks all trading orders with comprehensive status management.

### KotakNeoMarketData
Stores real-time market data with OHLCV information.

### KotakNeoHolding
Manages portfolio holdings with P&L tracking.

### KotakNeoAlert
Custom alert system for price, volume, and OI monitoring.

### KotakNeoOptionChain
Comprehensive option chain data with Greeks.

### KotakNeoAPILog
Detailed API call logging for debugging and monitoring.

## Setup

### 1. Install Dependencies
```bash
pip install requests django-crontab
```

### 2. Add to INSTALLED_APPS
Add `'KOTAK_NEO_API'` to your Django settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'KOTAK_NEO_API',
]
```

### 3. Configure Settings
Add Kotak Neo API credentials to your Django settings:

```python
# Kotak Neo API Settings
KOTAK_NEO_USER_ID = 'your_user_id'
KOTAK_NEO_API_KEY = 'your_api_key'
KOTAK_NEO_API_SECRET = 'your_api_secret'
```

### 4. Run Migrations
```bash
python manage.py makemigrations KOTAK_NEO_API
python manage.py migrate
```

### 5. Add Cron Jobs
```bash
python manage.py crontab add
```

## Usage

### API Integration

```python
from KOTAK_NEO_API.kotak_integration import KotakNeoAPI

# Initialize API (auto-authenticates)
api = KotakNeoAPI()

# Get market quotes
quotes = api.get_quote(['NIFTY', 'BANKNIFTY'])

# Place an order
order = api.place_order(
    tradingsymbol='NIFTY23DEC19000CE',
    transaction_type='BUY',
    quantity=1,
    price=100.50
)

# Get holdings
holdings = api.get_holdings()

# Get option chain
option_chain = api.get_option_chain('NIFTY')
```

### Admin Interface

Access the admin interface at `/admin/` to manage:

- **User Tokens**: View and manage authentication tokens
- **Instruments**: Browse and search trading instruments
- **Orders**: Monitor order status and history
- **Market Data**: View real-time market data
- **Holdings**: Track portfolio holdings
- **Alerts**: Manage trading alerts
- **API Logs**: Monitor API performance and errors

### Dashboard

Visit `/kotak/dashboard/` for a comprehensive overview including:

- Active tokens count
- Total holdings value
- Active alerts
- Recent orders
- API performance metrics

## Cron Jobs

The following automated tasks run during market hours (9:15 AM - 3:30 PM, Monday-Friday):

| Job | Frequency | Description |
|-----|-----------|-------------|
| Market Data Sync | Every 5 minutes | Sync real-time market data |
| Holdings Sync | Every 30 minutes | Update portfolio holdings |
| Alert Monitoring | Every 2 minutes | Check and trigger alerts |
| Option Chain Sync | Every 15 minutes | Update option chain data |
| Token Management | Hourly | Refresh expiring tokens |
| Data Cleanup | Daily at 2 AM | Remove old data |
| Instruments Sync | Daily at 6 AM | Update instrument list |

## API Endpoints

### Trading Endpoints
- `POST /kotak/api/place-order/` - Place new order
- `GET /kotak/api/get-quote/` - Get market quotes
- `GET /kotak/api/get-holdings/` - Get user holdings
- `GET /kotak/api/get-option-chain/` - Get option chain data

### Management Endpoints
- `GET /kotak/dashboard/` - Main dashboard
- `GET /kotak/orders/` - Order management
- `GET /kotak/holdings/` - Holdings view
- `GET /kotak/market-data/` - Market data view
- `GET /kotak/alerts/` - Alert management

## Alert System

Create custom alerts for:

- **Price Alerts**: Monitor specific price levels
- **Volume Alerts**: Track unusual volume activity
- **OI Alerts**: Monitor open interest changes
- **Custom Alerts**: Custom conditions

Alert conditions:
- Above/Below specific values
- Crosses above/below levels
- Equals exact values

## Error Handling

The system includes comprehensive error handling:

- Automatic token refresh on expiration
- API call retry mechanisms
- Detailed error logging
- Graceful degradation

## Security Features

- Secure token storage
- API call logging
- User authentication
- Admin-only access for sensitive operations

## Monitoring

Monitor system health through:

- API logs in admin interface
- Dashboard metrics
- Cron job execution logs
- Error tracking and alerts

## Development

### Adding New Features

1. **Models**: Add new models in `models.py`
2. **Admin**: Register models in `admin.py`
3. **API**: Extend `KotakNeoAPI` class
4. **Views**: Add views in `views.py`
5. **Cron**: Add cron jobs in `kotak_neo_cron.py`
6. **Templates**: Create templates in `templates/KOTAK_NEO_API/`

### Testing

```bash
# Run tests
python manage.py test KOTAK_NEO_API

# Test API integration
python manage.py shell
>>> from KOTAK_NEO_API.kotak_integration import KotakNeoAPI
>>> api = KotakNeoAPI()
>>> api.get_market_status()
```

## Troubleshooting

### Common Issues

1. **Token Expiration**: Check token status in admin
2. **API Errors**: Review API logs in admin
3. **Cron Jobs**: Check cron job status
4. **Data Sync**: Verify market hours

### Debug Mode

Enable debug logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'KOTAK_NEO_API': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the admin interface for logs
- Review the API documentation
- Contact the development team 