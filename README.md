# 🤖 Affiliate Bot - Marketing Automation Platform

An **automated affiliate marketing bot** designed to streamline commission tracking, performance analytics, and campaign management for affiliate programs with real-time notifications and comprehensive reporting.

## 🎯 Overview

This bot provides:
- ✅ Affiliate link generation
- ✅ Commission tracking
- ✅ Performance analytics
- ✅ Real-time notifications
- ✅ Campaign management
- ✅ User payouts
- ✅ Fraud detection

## 🏗️ Architecture

```
Affiliate Input
    ↓
Link Generator → Database
    ↓
Tracking System → Click/Conversion Monitoring
    ↓
Analytics Engine
    ↓
Commission Calculator → Reporting Dashboard
```

## 💰 Core Features

### 1. Affiliate Link Generation

```python
import hashlib
import secrets
from urllib.parse import urlencode

class AffiliateManager:
    @staticmethod
    def generate_affiliate_link(product_id, affiliate_id):
        """Generate unique affiliate tracking link"""
        tracking_param = secrets.token_urlsafe(16)
        
        params = {
            'aff_id': affiliate_id,
            'product': product_id,
            'token': tracking_param
        }
        
        affiliate_link = f"https://yoursite.com/product?{urlencode(params)}"
        return affiliate_link
    
    @staticmethod
    def generate_short_link(affiliate_link):
        """Generate short URL for sharing"""
        hash_obj = hashlib.md5(affiliate_link.encode())
        short_code = hash_obj.hexdigest()[:8]
        return f"https://aff.io/{short_code}"
```

### 2. Commission Tracking

```python
class CommissionTracker:
    def __init__(self, db):
        self.db = db
    
    def record_click(self, affiliate_id, product_id, user_ip):
        """Track click event"""
        click = {
            'affiliate_id': affiliate_id,
            'product_id': product_id,
            'user_ip': user_ip,
            'timestamp': datetime.now(),
            'converted': False,
        }
        
        self.db.clicks.insert_one(click)
        return click['_id']
    
    def record_conversion(self, click_id, sale_amount):
        """Record successful conversion"""
        self.db.clicks.update_one(
            {'_id': click_id},
            {
                '$set': {
                    'converted': True,
                    'conversion_amount': sale_amount,
                    'conversion_date': datetime.now()
                }
            }
        )
        
        # Calculate commission
        commission = self.calculate_commission(sale_amount)
        return commission
    
    def calculate_commission(self, amount, rate=0.1):
        """Calculate commission based on rate"""
        return amount * rate
```

### 3. Analytics Dashboard

```python
class AffiliateAnalytics:
    def __init__(self, db):
        self.db = db
    
    def get_affiliate_stats(self, affiliate_id, start_date, end_date):
        """Get performance metrics for affiliate"""
        pipeline = [
            {
                '$match': {
                    'affiliate_id': affiliate_id,
                    'timestamp': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_clicks': {'$sum': 1},
                    'conversions': {
                        '$sum': {'$cond': ['$converted', 1, 0]}
                    },
                    'total_commission': {
                        '$sum': {'$cond': ['$converted', '$commission', 0]}
                    },
                }
            }
        ]
        
        result = self.db.clicks.aggregate(pipeline)
        return list(result)[0]
    
    def get_conversion_rate(self, affiliate_id):
        """Calculate conversion rate percentage"""
        stats = self.get_affiliate_stats(affiliate_id)
        if stats['total_clicks'] == 0:
            return 0
        return (stats['conversions'] / stats['total_clicks']) * 100
    
    def get_top_products(self, affiliate_id, limit=10):
        """Get best performing products"""
        pipeline = [
            {'$match': {'affiliate_id': affiliate_id, 'converted': True}},
            {'$group': {
                '_id': '$product_id',
                'conversions': {'$sum': 1},
                'total_revenue': {'$sum': '$conversion_amount'}
            }},
            {'$sort': {'total_revenue': -1}},
            {'$limit': limit}
        ]
        
        return list(self.db.clicks.aggregate(pipeline))
```

### 4. Real-time Notifications

```python
from twilio.rest import Client

class NotificationService:
    def __init__(self, account_sid, auth_token):
        self.client = Client(account_sid, auth_token)
    
    def notify_conversion(self, affiliate_phone, amount):
        """Send SMS notification on conversion"""
        message = self.client.messages.create(
            body=f"🎉 New conversion! You earned ${amount:.2f} commission!",
            from_="+1234567890",
            to=affiliate_phone
        )
        return message.sid
    
    def notify_payout(self, affiliate_email, amount):
        """Send email notification for payout"""
        send_email(
            to=affiliate_email,
            subject="Payout Processed",
            body=f"Your payout of ${amount:.2f} has been processed."
        )
```

### 5. Fraud Detection

```python
class FraudDetector:
    """Detect suspicious affiliate activity"""
    
    SUSPICIOUS_THRESHOLD = 0.8  # 80% conversion rate
    
    def is_suspicious_click_pattern(self, affiliate_id):
        """Detect unusual click patterns"""
        clicks = list(self.db.clicks.find({
            'affiliate_id': affiliate_id,
            'timestamp': {'$gte': datetime.now() - timedelta(hours=1)}
        }))
        
        # Check for rapid clicks from same IP
        ip_counts = {}
        for click in clicks:
            ip = click['user_ip']
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        # If one IP has >10 clicks in 1 hour, suspect bot
        return any(count > 10 for count in ip_counts.values())
    
    def is_suspicious_conversion_rate(self, affiliate_id):
        """Detect unusually high conversion rates"""
        stats = self.get_affiliate_stats(affiliate_id)
        
        if stats['total_clicks'] < 100:
            return False  # Not enough data
        
        rate = stats['conversions'] / stats['total_clicks']
        return rate > self.SUSPICIOUS_THRESHOLD
    
    def flag_suspicious_account(self, affiliate_id, reason):
        """Flag account for manual review"""
        self.db.flagged_accounts.insert_one({
            'affiliate_id': affiliate_id,
            'reason': reason,
            'flagged_at': datetime.now(),
            'status': 'pending_review'
        })
```

### 6. Payment Processing

```python
from stripe import Stripe

class PaymentProcessor:
    def __init__(self, stripe_key):
        self.stripe = Stripe(stripe_key)
    
    def process_payout(self, affiliate_id, amount):
        """Process affiliate payout"""
        affiliate = self.db.affiliates.find_one({'_id': affiliate_id})
        
        try:
            payout = self.stripe.payouts.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                destination=affiliate['stripe_account_id']
            )
            
            # Record payout
            self.db.payouts.insert_one({
                'affiliate_id': affiliate_id,
                'amount': amount,
                'stripe_payout_id': payout.id,
                'status': 'processed',
                'timestamp': datetime.now()
            })
            
            return payout
        
        except Exception as e:
            # Record failed payout
            self.db.payouts.insert_one({
                'affiliate_id': affiliate_id,
                'amount': amount,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now()
            })
            raise
```

### 7. Automated Payouts

```python
from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def process_monthly_payouts():
    """Automated task to process monthly commissions"""
    
    # Get affiliates with pending earnings
    pipeline = [
        {
            '$match': {
                'converted': True,
                'paid': False,
                'conversion_date': {
                    '$lt': datetime.now() - timedelta(days=30)
                }
            }
        },
        {
            '$group': {
                '_id': '$affiliate_id',
                'total_commission': {'$sum': '$commission'}
            }
        }
    ]
    
    affiliates_to_pay = list(db.clicks.aggregate(pipeline))
    
    for affiliate in affiliates_to_pay:
        affiliate_id = affiliate['_id']
        amount = affiliate['total_commission']
        
        try:
            processor = PaymentProcessor(STRIPE_KEY)
            processor.process_payout(affiliate_id, amount)
            
            # Mark commissions as paid
            db.clicks.update_many(
                {'affiliate_id': affiliate_id, 'paid': False},
                {'$set': {'paid': True}}
            )
            
        except Exception as e:
            logger.error(f"Payout failed for {affiliate_id}: {e}")
```

## 🎨 Dashboard Features

```
Dashboard
├── Performance Metrics
│   ├── Total Clicks
│   ├── Conversions
│   ├── Conversion Rate
│   └── Total Earnings
├── Charts
│   ├── Daily clicks trend
│   ├── Top products
│   ├── Revenue by source
│   └── Commission breakdown
└── Reports
    ├── Monthly summary
    ├── Product performance
    ├── Channel analysis
    └── Export CSV/PDF
```

## 💡 Interview Questions

**Q: How would you detect click fraud?**
```
Answer:
1. Duplicate IP detection
2. Conversion rate outliers
3. Time-based pattern analysis
4. Device fingerprinting
5. Geographic anomalies
```

**Q: How to scale this for millions of affiliates?**
```
Answer:
- Distributed database (sharding)
- Cache layer (Redis)
- Event streaming (Kafka)
- Real-time analytics (ClickHouse)
- Load balancing
```

## 🌟 Portfolio Value

✅ Marketing automation
✅ Payment processing
✅ Fraud detection
✅ Real-time analytics
✅ Distributed systems
✅ API integration

## 📄 License

MIT License - Educational Use

---

**Tech Stack**: Python, MongoDB, Stripe, Celery, Redis

