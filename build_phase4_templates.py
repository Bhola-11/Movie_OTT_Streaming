import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. SUBSCRIPTIONS TEMPLATES
# ==============================================================================

plans_html = '''{% extends 'base.html' %}
{% block title %}Membership Plans & Pricing — CineVerse VIP{% endblock %}

{% block content %}
<div class="container" style="max-width: 1200px; padding-top: 2rem;">
  <div style="text-align: center; margin-bottom: 3.5rem;">
    <span class="badge badge-vip" style="margin-bottom: 0.75rem; font-size: 0.8rem;">CHOOSE YOUR PASS</span>
    <h1 style="font-size: 2.75rem; margin-bottom: 0.75rem;">Flexible Plans for Every Cinephile</h1>
    <p style="max-width: 600px; margin: 0 auto; font-size: 1.05rem;">Stream ad-free in 4K HDR with spatial audio across all your favorite devices. Cancel anytime with a single click.</p>
  </div>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 2rem;">
    {% for plan in plans %}
      <div style="background: var(--cv-bg-surface); border: 2px solid {% if plan.tier_code == 'VIP_4K' %}var(--cv-gold){% else %}var(--cv-border){% endif %}; border-radius: var(--cv-radius-lg); padding: 2.5rem 2rem; display: flex; flex-direction: column; justify-content: space-between; position: relative; transition: var(--cv-transition);" onmouseover="this.style.transform='translateY(-6px)';" onmouseout="this.style.transform='none';">
        {% if plan.tier_code == 'VIP_4K' %}
          <div style="position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #FFB800, #FF8A00); color: #000; font-weight: 800; font-size: 0.75rem; padding: 0.25rem 1rem; border-radius: var(--cv-radius-full); letter-spacing: 0.05em;">
            MOST POPULAR • 4K VIP
          </div>
        {% endif %}

        <div>
          <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">{{ plan.name }}</h3>
          <p style="font-size: 0.85rem; margin-bottom: 1.75rem; min-height: 40px;">{{ plan.description }}</p>

          <div style="margin-bottom: 2rem;">
            <span style="font-size: 3rem; font-weight: 900; font-family: var(--cv-font-display); color: #fff;">${{ plan.price_monthly }}</span>
            <span style="color: var(--cv-text-muted); font-size: 0.9rem;">/month</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.85rem; font-size: 0.9rem; border-top: 1px solid var(--cv-border); padding-top: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span>✓</span> Max Resolution: <strong style="color: #fff;">{{ plan.max_resolution }}</strong>
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span>✓</span> Concurrent Streams: <strong style="color: #fff;">{{ plan.max_screens }} Screens</strong>
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span>{% if plan.has_dolby_atmos %}✓{% else %}✕{% endif %}</span> Dolby Atmos Spatial Audio
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span>{% if plan.allows_offline_downloads %}✓{% else %}✕{% endif %}</span> Offline Mobile Downloads
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span>{% if plan.ad_free %}✓{% else %}✕{% endif %}</span> 100% Ad-Free Cinema
            </div>
          </div>
        </div>

        <div style="margin-top: 2.5rem;">
          <a href="{% url 'payments:checkout' %}?plan={{ plan.pk }}&cycle=MONTHLY" class="btn {% if plan.tier_code == 'VIP_4K' %}btn-gold{% else %}btn-primary{% endif %}" style="width: 100%;">
            Get {{ plan.name }}
          </a>
        </div>
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/subscriptions/plans.html', plans_html)

my_subscription_html = '''{% extends 'base.html' %}
{% block title %}My Subscription — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 900px; padding-top: 2rem;">
  <div style="margin-bottom: 2.5rem;">
    <h1>My Subscription & Billing</h1>
    <p>View your active streaming plan and billing statements.</p>
  </div>

  {% if subscription %}
    <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2.5rem; margin-bottom: 2.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
        <div>
          <span class="badge badge-vip" style="margin-bottom: 0.5rem;">ACTIVE MEMBERSHIP</span>
          <h2>{{ subscription.plan.name }}</h2>
          <p style="font-size: 0.95rem;">${{ subscription.plan.price_monthly }}/mo • Billed {{ subscription.billing_cycle }}</p>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.85rem; color: var(--cv-text-muted);">Current Period Ends</div>
          <div style="font-weight: 700; color: #fff; font-size: 1.1rem;">{{ subscription.expires_at|date:"F d, Y" }}</div>
        </div>
      </div>

      <div style="display: flex; gap: 1rem; border-top: 1px solid var(--cv-border); padding-top: 1.5rem;">
        <a href="{% url 'subscriptions:plans' %}" class="btn btn-secondary btn-sm">Change Plan Tier</a>
        {% if subscription.auto_renew %}
          <form method="post" action="{% url 'subscriptions:cancel' %}" onsubmit="return confirm('Cancel auto-renew?');">
            {% csrf_token %}
            <button type="submit" class="btn btn-outline btn-sm" style="color: #FF5E62; border-color: rgba(255,94,98,0.4);">Cancel Renewal</button>
          </form>
        {% endif %}
      </div>
    </div>
  {% else %}
    <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 3rem; text-align: center; margin-bottom: 2.5rem;">
      <h3 style="margin-bottom: 0.75rem;">No Active Subscription Found</h3>
      <p style="margin-bottom: 1.5rem;">Subscribe to unlock unlimited 4K streaming and downloads.</p>
      <a href="{% url 'subscriptions:plans' %}" class="btn btn-primary">Browse VIP Plans</a>
    </div>
  {% endif %}

  <!-- Invoices History -->
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
    <h3>Billing Invoices</h3>
    <a href="{% url 'payments:invoice_list' %}" style="font-size: 0.85rem; color: var(--cv-primary);">View All Invoices ›</a>
  </div>

  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); overflow: hidden;">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
      <thead>
        <tr style="background: rgba(255,255,255,0.03); border-bottom: 1px solid var(--cv-border); text-align: left;">
          <th style="padding: 1rem;">Invoice Number</th>
          <th style="padding: 1rem;">Date</th>
          <th style="padding: 1rem;">Amount</th>
          <th style="padding: 1rem; text-align: right;">PDF Statement</th>
        </tr>
      </thead>
      <tbody>
        {% for inv in recent_invoices %}
          <tr style="border-bottom: 1px solid var(--cv-border);">
            <td style="padding: 1rem; font-weight: 600; color: #fff;">{{ inv.invoice_number }}</td>
            <td style="padding: 1rem; color: var(--cv-text-muted);">{{ inv.issued_at|date:"M d, Y" }}</td>
            <td style="padding: 1rem; color: #fff;">${{ inv.total_amount }}</td>
            <td style="padding: 1rem; text-align: right;">
              <a href="{{ inv.get_absolute_url }}" class="btn btn-outline btn-sm" style="font-size: 0.75rem;">📥 Download PDF</a>
            </td>
          </tr>
        {% empty %}
          <tr>
            <td colspan="4" style="padding: 2rem; text-align: center; color: var(--cv-text-muted);">No invoices generated yet.</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
'''
write('templates/subscriptions/my_subscription.html', my_subscription_html)

# ==============================================================================
# 2. PAYMENTS CHECKOUT & SUCCESS TEMPLATES
# ==============================================================================

checkout_html = '''{% extends 'base.html' %}
{% block title %}Checkout — CineVerse VIP Subscription{% endblock %}

{% block content %}
<div class="container" style="max-width: 800px; padding-top: 2rem;">
  <div style="margin-bottom: 2rem;">
    <h1>Confirm Your Subscription</h1>
    <p>Complete checkout to unlock high-definition streaming instantly.</p>
  </div>

  <div style="display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem;">
    <!-- Payment Form -->
    <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 2rem;">
      <h3 style="margin-bottom: 1.5rem;">Payment Method</h3>

      <form method="post">
        {% csrf_token %}
        <input type="hidden" name="plan_id" value="{{ plan.pk }}">
        <input type="hidden" name="billing_cycle" value="{{ billing_cycle }}">

        <div class="form-group">
          <label class="form-label">Cardholder Full Name</label>
          <input type="text" class="form-input" value="{{ user.full_name }}" required>
        </div>

        <div class="form-group">
          <label class="form-label">Card Number</label>
          <input type="text" class="form-input" placeholder="4242 •••• •••• 4242" value="4242 4242 4242 4242" required>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Expiry</label>
            <input type="text" class="form-input" placeholder="MM/YY" value="12/28" required>
          </div>
          <div class="form-group">
            <label class="form-label">CVV / CVC</label>
            <input type="password" class="form-input" placeholder="123" value="789" required>
          </div>
        </div>

        <div style="background: rgba(0, 223, 154, 0.08); border: 1px solid rgba(0, 223, 154, 0.3); border-radius: var(--cv-radius-sm); padding: 0.75rem; margin-bottom: 1.5rem; font-size: 0.8rem; color: var(--cv-accent);">
          🔒 256-bit SSL encrypted sandbox transaction.
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%; padding: 0.85rem; font-size: 1rem;">
          Authorize & Pay ${{ plan.price_monthly }}
        </button>
      </form>
    </div>

    <!-- Order Summary -->
    <div>
      <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-lg); padding: 1.75rem;">
        <h4 style="margin-bottom: 1.25rem;">Order Summary</h4>

        <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; font-size: 0.9rem;">
          <span style="color: var(--cv-text-muted);">{{ plan.name }} (Monthly)</span>
          <span style="color: #fff; font-weight: 600;">${{ plan.price_monthly }}</span>
        </div>

        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; font-size: 0.9rem;">
          <span style="color: var(--cv-text-muted);">Estimated Tax</span>
          <span style="color: #fff; font-weight: 600;">$0.00</span>
        </div>

        <div style="display: flex; justify-content: space-between; border-top: 1px solid var(--cv-border); padding-top: 1rem; font-size: 1.15rem; font-weight: 700; color: #fff;">
          <span>Total Today:</span>
          <span style="color: var(--cv-gold);">${{ plan.price_monthly }}</span>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/payments/checkout.html', checkout_html)

success_html = '''{% extends 'base.html' %}
{% block title %}Payment Successful — CineVerse{% endblock %}

{% block content %}
<div class="auth-wrapper">
  <div class="auth-card" style="text-align: center; max-width: 550px;">
    <div style="font-size: 3.5rem; margin-bottom: 1rem;">🎉</div>
    <span class="badge badge-creator" style="margin-bottom: 0.5rem;">PAYMENT CONFIRMED</span>
    <h2 style="margin-bottom: 0.5rem;">Welcome to CineVerse VIP!</h2>
    <p style="margin-bottom: 2rem;">Your transaction <strong>{{ transaction.transaction_reference }}</strong> of ${{ transaction.amount }} was authorized successfully.</p>

    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
      <a href="{% url 'movies:browse' %}" class="btn btn-primary btn-lg">
        Start Streaming Now
      </a>
      <a href="{{ transaction.invoice.get_absolute_url }}" class="btn btn-secondary">
        📥 Download Official PDF Tax Invoice
      </a>
    </div>
  </div>
</div>
{% endblock %}
'''
write('templates/payments/success.html', success_html)

invoice_list_html = '''{% extends 'base.html' %}
{% block title %}Tax Invoices — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 900px; padding-top: 2rem;">
  <h1>Billing & Invoices</h1>
  <p style="margin-bottom: 2rem;">Complete record of your CineVerse billing receipts.</p>

  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); overflow: hidden;">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
      <thead>
        <tr style="background: rgba(255,255,255,0.03); border-bottom: 1px solid var(--cv-border); text-align: left;">
          <th style="padding: 1rem;">Invoice Number</th>
          <th style="padding: 1rem;">Date</th>
          <th style="padding: 1rem;">Total Amount</th>
          <th style="padding: 1rem; text-align: right;">Download</th>
        </tr>
      </thead>
      <tbody>
        {% for inv in invoices %}
          <tr style="border-bottom: 1px solid var(--cv-border);">
            <td style="padding: 1rem; font-weight: 600; color: #fff;">{{ inv.invoice_number }}</td>
            <td style="padding: 1rem; color: var(--cv-text-muted);">{{ inv.issued_at|date:"M d, Y" }}</td>
            <td style="padding: 1rem; color: #fff;">${{ inv.total_amount }}</td>
            <td style="padding: 1rem; text-align: right;">
              <a href="{{ inv.get_absolute_url }}" class="btn btn-outline btn-sm">📥 Download PDF</a>
            </td>
          </tr>
        {% empty %}
          <tr>
            <td colspan="4" style="padding: 2rem; text-align: center; color: var(--cv-text-muted);">No invoices found.</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
'''
write('templates/payments/invoice_list.html', invoice_list_html)

# ==============================================================================
# 3. NOTIFICATIONS INBOX TEMPLATE
# ==============================================================================

inbox_html = '''{% extends 'base.html' %}
{% block title %}Notification Center — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 800px; padding-top: 2rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div>
      <h1>Notification Center</h1>
      <p>Updates on new releases, billing statements, and account security.</p>
    </div>
    <form method="post" action="{% url 'notifications:mark_all_read' %}">
      {% csrf_token %}
      <button type="submit" class="btn btn-outline btn-sm">Mark All as Read</button>
    </form>
  </div>

  <div style="display: flex; flex-direction: column; gap: 1rem;">
    {% for notif in notifications %}
      <div style="display: flex; justify-content: space-between; align-items: center; background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); padding: 1.25rem; {% if not notif.is_read %}border-left: 4px solid var(--cv-primary);{% endif %}">
        <div>
          <div style="font-weight: 700; color: #fff; margin-bottom: 0.25rem;">{{ notif.title }}</div>
          <p style="font-size: 0.875rem; margin-bottom: 0.4rem;">{{ notif.message }}</p>
          <div style="font-size: 0.75rem; color: var(--cv-text-muted);">{{ notif.created_at|timesince }} ago</div>
        </div>
        {% if notif.target_url %}
          <a href="{{ notif.target_url }}" class="btn btn-secondary btn-sm">View Details</a>
        {% endif %}
      </div>
    {% empty %}
      <div style="padding: 4rem; text-align: center; background: var(--cv-bg-surface); border-radius: var(--cv-radius-md); color: var(--cv-text-muted);">
        No notifications in your inbox.
      </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''
write('templates/notifications/inbox.html', inbox_html)

print("Phase 4 templates written.")
