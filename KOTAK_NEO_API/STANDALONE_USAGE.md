# Kotak Neo API Standalone Usage

## Overview

The Kotak Neo API can be used in two modes:

1. **Django Mode**: Full integration with Django models, admin interface, and database storage
2. **Standalone Mode**: Lightweight version that doesn't require Django or database setup

## Standalone Mode

### Features

- ✅ **No Django Dependencies**: Can run independently without Django
- ✅ **No Database Required**: All data is handled in memory
- ✅ **Real API Calls**: Makes actual HTTP requests to Kotak Neo servers
- ✅ **Comprehensive Logging**: All API calls are logged with timestamps
- ✅ **Error Handling**: Built-in error handling for network and API issues
- ✅ **Auto-Authentication**: Automatic token management and refresh
- ✅ **Mock Tokens**: Uses mock tokens for testing without real credentials

### Installation

No additional installation required. The standalone version uses only standard Python libraries:

```python
import requests
import json
import time
import logging
from datetime import datetime, timedelta
```

### Basic Usage

```python
from KOTAK_NEO_API.kotak_integration_standalone import KotakNeoAPI

# Initialize API
api = KotakNeoAPI(
    user_id='your_user_id',
    api_key='your_api_key',
    api_secret='your_api_secret'
)

# Check token status
print(f"Token valid: {api.user_token.is_valid}")
print(f"Token expired: {api.user_token.is_expired}")
```

### API Methods

#### Market Data

```python
# Get market status
status = api.get_market_status()

# Get quotes for instruments
quotes = api.get_quote(['NIFTY', 'BANKNIFTY'])

# Get historical data
historical = api.get_historical_data(
    instrument_token='NIFTY',
    from_date='2024-01-01',
    to_date='2024-01-31',
    interval='1D'
)

# Get option chain
option_chain = api.get_option_chain('NIFTY')
```

#### Order Management

```python
# Place order
order = api.place_order(
    tradingsymbol='NIFTY',
    transaction_type='BUY',
    quantity=1,
    product='NRML',
    order_type='LIMIT',
    price=19500.0
)

# Modify order
modified = api.modify_order(order_id='12345', price=19550.0)

# Cancel order
cancelled = api.cancel_order(order_id='12345')

# Get orders
orders = api.get_orders()
```

#### Portfolio

```python
# Get holdings
holdings = api.get_holdings()

# Get positions
positions = api.get_positions()
```

#### Instruments

```python
# Get instruments
instruments = api.get_instruments(exchange='NSE')
```

#### Sync Operations

```python
# Sync holdings (standalone mode just logs)
api.sync_holdings()

# Sync market data
api.sync_market_data(['NIFTY', 'BANKNIFTY', 'RELIANCE'])
```

### Error Handling

The API includes comprehensive error handling:

```python
try:
    quotes = api.get_quote(['NIFTY'])
    print(f"Quotes: {quotes}")
except Exception as e:
    print(f"Error getting quotes: {e}")
    # Handle error appropriately
```

### Logging

All API calls are automatically logged:

```
2025-08-03 10:25:33,955 - INFO - API Call: GET /market/status - Status: 200 - Time: 1.337s
2025-08-03 10:25:34,147 - INFO - API Call: POST /market/quotes - Status: 403 - Time: 0.190s
```

### Configuration

You can configure logging level:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Testing

Run the standalone test:

```bash
python test_kotak_standalone.py
```

Run the usage example:

```bash
python example_kotak_usage.py
```

### File Structure

```
KOTAK_NEO_API/
├── kotak_integration_standalone.py  # Standalone API class
├── kotak_integration.py             # Django-integrated API class
├── models.py                        # Django models
├── admin.py                         # Django admin
├── views.py                         # Django views
├── urls.py                          # Django URLs
├── kotak_neo_cron.py               # Cron jobs
└── migrations/                      # Django migrations

# Test files
test_kotak_standalone.py            # Standalone tests
example_kotak_usage.py              # Usage examples
test_kotak_api.py                   # Django integration tests
```

### Comparison: Standalone vs Django Mode

| Feature | Standalone | Django Mode |
|---------|------------|-------------|
| Dependencies | Minimal (requests, json, time, logging) | Full Django stack |
| Database | None required | PostgreSQL/MySQL/SQLite |
| Data Storage | In-memory only | Persistent database |
| Admin Interface | None | Full Django admin |
| Web Interface | None | Full Django views |
| Cron Jobs | Manual execution | Automated with django-crontab |
| Token Management | Mock tokens | Database-stored tokens |
| API Logging | Console logging | Database logging |
| Error Handling | Basic | Comprehensive with database |
| Scalability | Single process | Multi-process with database |

### Use Cases

#### Standalone Mode
- ✅ **Scripts**: Automated trading scripts
- ✅ **Testing**: API testing without database setup
- ✅ **Prototyping**: Quick API integration testing
- ✅ **CLI Tools**: Command-line trading tools
- ✅ **Microservices**: Lightweight API services

#### Django Mode
- ✅ **Web Applications**: Full web interface
- ✅ **Admin Management**: Database-backed admin interface
- ✅ **Multi-user**: Support for multiple users
- ✅ **Data Persistence**: Historical data storage
- ✅ **Automated Tasks**: Cron jobs and background tasks
- ✅ **Analytics**: Data analysis and reporting

### Migration Between Modes

#### From Standalone to Django

1. Install Django and database
2. Run migrations: `python manage.py migrate`
3. Update imports to use Django models
4. Configure settings and credentials

#### From Django to Standalone

1. Extract the standalone API class
2. Remove Django dependencies
3. Update error handling for console logging
4. Test with mock credentials

### Security Considerations

- ✅ **Credentials**: Store API credentials securely
- ✅ **Environment Variables**: Use environment variables for secrets
- ✅ **Token Management**: Implement proper token refresh
- ✅ **Error Logging**: Avoid logging sensitive data
- ✅ **Rate Limiting**: Implement API rate limiting
- ✅ **SSL/TLS**: Always use HTTPS for API calls

### Best Practices

1. **Error Handling**: Always wrap API calls in try-catch blocks
2. **Logging**: Use appropriate log levels (INFO, WARNING, ERROR)
3. **Rate Limiting**: Don't make too many API calls too quickly
4. **Token Management**: Let the API handle token refresh automatically
5. **Testing**: Test with mock data before using real credentials
6. **Documentation**: Document your API usage patterns

### Troubleshooting

#### Common Issues

1. **Import Errors**: Make sure Python path includes the project directory
2. **Network Errors**: Check internet connection and API endpoint availability
3. **Authentication Errors**: Verify API credentials are correct
4. **Rate Limiting**: Implement delays between API calls
5. **Token Expiry**: The API handles token refresh automatically

#### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Examples

See the following files for complete examples:

- `example_kotak_usage.py`: Basic usage examples
- `test_kotak_standalone.py`: Comprehensive tests
- `KOTAK_NEO_API/kotak_integration_standalone.py`: Complete API implementation

### Support

For issues and questions:

1. Check the logging output for error details
2. Verify API credentials and endpoints
3. Test with the provided example scripts
4. Review the Django integration for advanced features

---

**Note**: The standalone mode is perfect for quick testing and development. For production applications with multiple users and data persistence, use the Django mode. 