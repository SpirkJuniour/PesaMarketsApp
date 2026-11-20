import re
from decimal import Decimal
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, OTPVerification, Portfolio, Asset, Order, Transaction, CashTransfer
from .data import ASSETS, EXCHANGE_RATES

# Common Tailwind widget styling helper
TW_INPUT_CLASSES = (
    "w-full px-4 py-2.5 rounded-2xl bg-neutral-50 dark:bg-dark-800 "
    "border border-[#DDDDDD] dark:border-dark-750 text-neutral-900 dark:text-white "
    "text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-[#4169E1] transition-all"
)

TW_SELECT_CLASSES = (
    "w-full px-4 py-2.5 rounded-2xl bg-neutral-50 dark:bg-dark-800 "
    "border border-[#DDDDDD] dark:border-dark-750 text-neutral-900 dark:text-white "
    "text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-[#4169E1] transition-all"
)

# 1. Login Form with dual username/email resolution and validation
class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username or Email",
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'username or name@domain.com',
            'class': TW_INPUT_CLASSES,
            'autocomplete': 'username',
            'id': 'id_username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': TW_INPUT_CLASSES,
            'autocomplete': 'current-password',
            'id': 'id_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label="Keep me signed in on this device"
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        if 'data' in kwargs and kwargs['data']:
            data = kwargs['data'].copy()
            if 'username_or_email' in data and 'username' not in data:
                data['username'] = data['username_or_email']
            if 'remember_me' not in data:
                data['remember_me'] = True
            kwargs['data'] = data
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('username', '').strip()
        password = cleaned_data.get('password', '')

        if identifier and password:
            # 1. Attempt standard username authentication
            user = authenticate(self.request, username=identifier, password=password)
            
            # 2. If not authenticated, attempt case-insensitive username or email lookup
            if user is None:
                user_match = (
                    User.objects.filter(username__iexact=identifier).first()
                    or User.objects.filter(email__iexact=identifier).first()
                )
                if user_match and user_match.check_password(password):
                    user = user_match

            if user is None:
                # Check if user exists with matching password but inactive
                inactive_user = (
                    User.objects.filter(username__iexact=identifier).first()
                    or User.objects.filter(email__iexact=identifier).first()
                )
                if inactive_user and inactive_user.check_password(password) and not inactive_user.is_active:
                    raise forms.ValidationError("This user account is currently deactivated.")
                raise forms.ValidationError(
                    "Invalid username or password. Please verify your credentials."
                )
            elif not user.is_active:
                raise forms.ValidationError("This user account is currently deactivated.")

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return self.user_cache


# 2. Trader Registration Form
class TraderRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Richard', 'class': TW_INPUT_CLASSES})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Cooper', 'class': TW_INPUT_CLASSES})
    )
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Choose a username', 'class': TW_INPUT_CLASSES})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'john@pesamarkets.com', 'class': TW_INPUT_CLASSES})
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+254 712 345 678', 'class': TW_INPUT_CLASSES})
    )
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': TW_INPUT_CLASSES})
    )
    confirm_password = forms.CharField(
        min_length=6,
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': TW_INPUT_CLASSES})
    )
    terms_confirmed = forms.BooleanField(
        required=False,
        initial=True
    )
    marketing_opt_in = forms.BooleanField(
        required=False,
        initial=True
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        if 'data' in kwargs and kwargs['data']:
            data = kwargs['data'].copy()
            if 'phone_number' in data and 'phone' not in data:
                data['phone'] = data['phone_number']
            if 'username' not in data and data.get('email'):
                raw_name = data.get('email').split('@')[0]
                clean_base = re.sub(r'[^a-zA-Z0-9_]', '_', raw_name) or 'trader'
                candidate = clean_base
                cnt = 1
                while User.objects.filter(username__iexact=candidate).exists():
                    candidate = f"{clean_base}_{cnt}"
                    cnt += 1
                data['username'] = candidate
            if not data.get('confirm_password') and data.get('password'):
                data['confirm_password'] = data.get('password')
            kwargs['data'] = data
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not phone:
            return ''
        phone = phone.strip()
        clean_num = re.sub(r'[\s\-\(\)]', '', phone)
        if clean_num and not re.match(r'^\+?[0-9]{7,15}$', clean_num):
            raise forms.ValidationError("Please enter a valid phone number (e.g. +254 712 345 678) or leave blank.")
        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username is required. Please choose a username.")

        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, dots, and underscores.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(f"Username '{username}' is already registered.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(f"An account with email '{email}' already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd_confirm = cleaned_data.get('confirm_password')

        if pwd and pwd_confirm and pwd != pwd_confirm:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            phone = self.cleaned_data.get('phone', '').strip()
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': phone,
                    'job_title': '',
                    'industry': '',
                    'tier': 'Free Tier',
                    'cash_balance_usd': Decimal('0.00'),
                    'otp_enabled': True,
                    'email_verified': False,
                    'phone_verified': False
                }
            )
            profile.phone_number = phone
            profile.otp_enabled = True
            profile.save()
            user.profile = profile
        return user


# 3. OTP Verification Form
class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '••••••',
            'maxlength': '6',
            'class': (
                "w-56 text-center text-2xl font-black font-mono tracking-widest py-3 px-4 rounded-2xl "
                "bg-neutral-50 dark:bg-dark-800 border-2 border-[#DDDDDD] dark:border-dark-750 text-neutral-900 "
                "dark:text-white focus:outline-none focus:border-[#4169E1] transition-all"
            ),
            'autofocus': True,
            'id': 'id_otp_code'
        })
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip().replace(' ', '')
        if not re.match(r'^\d{6}$', code):
            raise forms.ValidationError("Verification code must be exactly 6 numeric digits.")
        return code

    def verify_otp(self, user, purpose='login'):
        code = self.cleaned_data.get('otp_code')
        if not user or not code:
            return False

        otp = OTPVerification.objects.filter(
            user=user,
            otp_code=code,
            is_used=False
        ).order_by('-created_at').first()

        if otp and otp.is_valid():
            otp.mark_used()
            if hasattr(user, 'profile') and user.profile:
                user.profile.email_verified = True
                if user.profile.phone_number:
                    user.profile.phone_verified = True
                user.profile.save()
            return True
        return False


# 4. User Profile & Account Edit Forms
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TW_INPUT_CLASSES}),
            'last_name': forms.TextInput(attrs={'class': TW_INPUT_CLASSES}),
            'email': forms.EmailInput(attrs={'class': TW_INPUT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use by another trader.")
        return email


class UserProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'preferred_currency', 'otp_enabled']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': TW_INPUT_CLASSES}),
            'bio': forms.Textarea(attrs={'class': TW_INPUT_CLASSES, 'rows': 3, 'placeholder': 'Tell other investors about your investment philosophy...'}),
            'preferred_currency': forms.Select(
                choices=[('USD', 'USD - US Dollar'), ('KES', 'KES - Kenya Shilling'), ('GBP', 'GBP - British Pound'), ('JPY', 'JPY - Japanese Yen')],
                attrs={'class': TW_SELECT_CLASSES}
            ),
            'otp_enabled': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#4169E1] rounded focus:ring-[#4169E1]'}),
        }

    def __init__(self, *args, **kwargs):
        if 'data' in kwargs and kwargs['data']:
            data = kwargs['data'].copy()
            if 'phone' in data and 'phone_number' not in data:
                data['phone_number'] = data['phone']
            kwargs['data'] = data
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].required = False
        self.fields['bio'].required = False
        self.fields['preferred_currency'].required = False
        self.fields['otp_enabled'].required = False


# 5. Password Change Form
class PasswordChangeCustomForm(forms.Form):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': TW_INPUT_CLASSES})
    )
    new_password = forms.CharField(
        label="New Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': TW_INPUT_CLASSES})
    )
    confirm_new_password = forms.CharField(
        label="Confirm New Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': TW_INPUT_CLASSES})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_pwd = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_pwd):
            raise forms.ValidationError("Current password is incorrect.")
        return old_pwd

    def clean(self):
        cleaned_data = super().clean()
        new_pwd = cleaned_data.get('new_password')
        confirm_pwd = cleaned_data.get('confirm_new_password')
        old_pwd = cleaned_data.get('old_password')

        if new_pwd and confirm_pwd and new_pwd != confirm_pwd:
            self.add_error('confirm_new_password', "New passwords do not match.")

        if new_pwd and old_pwd and new_pwd == old_pwd:
            self.add_error('new_password', "New password cannot be identical to your old password.")

        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()
        return self.user


# 6. Trade Order Form (Equities, Sovereign Bonds, T-Bills, Commodities)
class TradeOrderForm(forms.Form):
    ACTION_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    ORDER_TYPE_CHOICES = (
        ('MARKET', 'Market Execution'),
        ('LIMIT', 'Limit Order'),
        ('STOP', 'Stop-Loss Order'),
    )

    symbol = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': TW_INPUT_CLASSES, 'placeholder': 'e.g. SCOM or NVDA'}))
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'class': TW_SELECT_CLASSES}))
    order_type = forms.ChoiceField(choices=ORDER_TYPE_CHOICES, initial='MARKET', widget=forms.Select(attrs={'class': TW_SELECT_CLASSES}))
    quantity = forms.DecimalField(max_digits=18, decimal_places=8, min_value=Decimal('0.00000001'), widget=forms.NumberInput(attrs={'class': TW_INPUT_CLASSES, 'placeholder': '1.0'}))
    price = forms.DecimalField(max_digits=12, decimal_places=2, required=False, min_value=Decimal('0.01'), widget=forms.NumberInput(attrs={'class': TW_INPUT_CLASSES, 'placeholder': 'Market price'}))
    face_value = forms.DecimalField(max_digits=15, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': TW_INPUT_CLASSES, 'placeholder': '50000'}))
    bid_yield = forms.DecimalField(max_digits=6, decimal_places=4, required=False, widget=forms.NumberInput(attrs={'class': TW_INPUT_CLASSES, 'placeholder': '14.5000'}))
    channel = forms.CharField(max_length=50, required=False, initial='CBK_DHOWCSD', widget=forms.TextInput(attrs={'class': TW_INPUT_CLASSES}))

    def __init__(self, user=None, portfolio=None, *args, **kwargs):
        self.user = user
        self.portfolio = portfolio
        super().__init__(*args, **kwargs)

    def clean_symbol(self):
        sym = self.cleaned_data.get('symbol', '').upper().strip()
        if sym not in ASSETS:
            # Check DB
            if not Asset.objects.filter(symbol=sym).exists():
                raise forms.ValidationError(f"Asset '{sym}' is not listed on PesaMarkets.")
        return sym

    def clean(self):
        cleaned_data = super().clean()
        sym = cleaned_data.get('symbol')
        action = cleaned_data.get('action')
        quantity = cleaned_data.get('quantity')
        order_type = cleaned_data.get('order_type')
        limit_price = cleaned_data.get('price')

        if not sym or not quantity:
            return cleaned_data

        asset_info = ASSETS.get(sym)
        unit_price = limit_price or (Decimal(str(asset_info['price'])) if asset_info else Decimal('100.0'))
        cleaned_data['resolved_price'] = unit_price

        # Check funds/holdings if portfolio is provided
        if self.portfolio:
            currency = asset_info.get('currency', 'USD') if asset_info else 'USD'
            fx = Decimal(str(EXCHANGE_RATES.get(currency, 1.0)))
            total_cost_local = unit_price * quantity
            total_cost_usd = round(total_cost_local / fx, 2)
            cleaned_data['cost_usd'] = total_cost_usd

            if action == 'BUY':
                if self.portfolio.cash_balance_usd < total_cost_usd:
                    raise forms.ValidationError(
                        f"Insufficient available cash. Required: ${total_cost_usd} USD, Available: ${self.portfolio.cash_balance_usd} USD."
                    )
            elif action == 'SELL':
                holdings = {h['symbol']: h['shares'] for h in self.portfolio.get_holdings()}
                owned_shares = Decimal(str(holdings.get(sym, 0)))
                if owned_shares < quantity:
                    raise forms.ValidationError(
                        f"Insufficient holdings to sell. You currently own {owned_shares} shares of {sym}."
                    )

        return cleaned_data


# 7. Cash Deposit and Withdrawal Form
class CashTransferForm(forms.ModelForm):
    account_or_phone = forms.CharField(
        max_length=50,
        required=True,
        label="M-PESA Phone Number or Bank Account",
        widget=forms.TextInput(attrs={'placeholder': '+254 712 345 678', 'class': TW_INPUT_CLASSES})
    )

    class Meta:
        model = CashTransfer
        fields = ['transfer_type', 'amount', 'method', 'account_or_phone']
        widgets = {
            'transfer_type': forms.Select(attrs={'class': TW_SELECT_CLASSES}),
            'amount': forms.NumberInput(attrs={'class': TW_INPUT_CLASSES, 'placeholder': '100.00', 'min': '1'}),
            'method': forms.Select(attrs={'class': TW_SELECT_CLASSES}),
        }

    def __init__(self, portfolio=None, *args, **kwargs):
        self.portfolio = portfolio
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= Decimal('0.00'):
            raise forms.ValidationError("Transfer amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        ttype = cleaned_data.get('transfer_type')
        amount = cleaned_data.get('amount')

        if ttype == 'WITHDRAWAL' and amount and self.portfolio:
            if self.portfolio.cash_balance_usd < amount:
                raise forms.ValidationError(
                    f"Insufficient funds for withdrawal. Available: ${self.portfolio.cash_balance_usd} USD, Requested: ${amount} USD."
                )

        return cleaned_data

    def execute(self):
        if not self.portfolio:
            raise ValueError("Portfolio must be provided to execute transfer.")
        
        transfer = self.save(commit=False)
        transfer.portfolio = self.portfolio
        transfer.status = 'COMPLETED'
        transfer.save()

        if transfer.transfer_type == 'DEPOSIT':
            self.portfolio.deposit(transfer.amount)
        elif transfer.transfer_type == 'WITHDRAWAL':
            self.portfolio.withdraw(transfer.amount)

        return transfer


# 8. Asset Search & Category Filter Form
class AssetSearchFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Filter listings by symbol, company...', 'class': TW_INPUT_CLASSES})
    )
    category = forms.ChoiceField(
        required=False,
        choices=[
            ('all', 'All Markets'),
            ('top50', 'Top 50 Best Companies'),
            ('warning', 'At Risk / Warning'),
            ('contenders', 'Contenders Queue'),
            ('usa', 'USA (NASDAQ/NYSE/US Treasury)'),
            ('uk', 'UK (LSE/UK DMO)'),
            ('kenya', 'Kenya (NSE/CBK)'),
            ('japan', 'Japan (Tokyo TSE/MOF)'),
            ('tbills', 'Treasury Bills (T-Bills)'),
            ('bonds', 'Sovereign Bonds & Gilts'),
            ('commodities', 'Commodities'),
            ('gainers', 'Top Gainers'),
            ('losers', 'Top Dips'),
        ],
        widget=forms.Select(attrs={'class': TW_SELECT_CLASSES})
    )
