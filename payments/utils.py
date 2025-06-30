from urllib.parse import urlencode


# utils/esewa.py
def initiate_esewa_payment(payment):
    payload = {
        "amount": str(payment.total_amount),
        "product_code": f"ORDER{payment.order.id}",
        "transaction_uuid": f"TX-{payment.id}",
        # etc.
    }
    payment.transaction_id = payload["transaction_uuid"]
    payment.save()
    return {
        "payment_gateway": "esewa",
        "payload": payload,
    }


def build_esewa_payment_url(payment):
    # base_url = "https://uat.esewa.com.np/epay/main"
    base_url = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"

    params = {
        "tAmt": payment.amount,
        "amt": payment.amount,
        "txAmt": 0,
        "psc": 0,
        "pdc": 0,
        "scd": "YourMerchantCode",
        "pid": str(payment.transaction_id),
        "su": f"https://yourdomain.com/esewa/success?pid={payment.transaction_id}",
        "fu": f"https://yourdomain.com/esewa/failure?pid={payment.transaction_id}",
    }
    return f"{base_url}?{urlencode(params)}"
