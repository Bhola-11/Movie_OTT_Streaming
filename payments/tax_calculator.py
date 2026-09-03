from decimal import Decimal

class InternationalTaxCalculator:
    """
    Computes country-level GST, VAT, and US sales tax for digital streaming subscriptions.
    """
    TAX_RATES = {
        'United States': Decimal('0.00'),   # Digital SaaS exempt in many states
        'United Kingdom': Decimal('0.20'),  # 20% VAT
        'European Union': Decimal('0.21'),  # 21% Average VAT
        'India': Decimal('0.18'),           # 18% GST for digital services
        'Canada': Decimal('0.05'),          # 5% Federal GST
        'Australia': Decimal('0.10'),       # 10% GST
        'Singapore': Decimal('0.09'),       # 9% GST
        'Japan': Decimal('0.10'),           # 10% JCT
    }

    @classmethod
    def calculate_tax(cls, subtotal_amount, country='United States'):
        subtotal = Decimal(str(subtotal_amount))
        rate = cls.TAX_RATES.get(country, Decimal('0.00'))
        tax_amount = round(subtotal * rate, 2)
        total_amount = round(subtotal + tax_amount, 2)
        return {
            'subtotal': subtotal,
            'tax_rate_percentage': float(rate * 100),
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'jurisdiction': country
        }
