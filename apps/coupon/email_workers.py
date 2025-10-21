# apps/coupons/email_workers.py
import threading
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import Template, Context

def _render(template_str, ctx):
    return Template(template_str).render(Context(ctx))

def send_coupons_in_background(*, coupons, users, template=None, from_email="noreply@yourdomain.com"):
    """
    Spawns a thread that sends email to each user using the selected template.
    """
    def _task():
        with get_connection() as conn:
            # helpful single item for templates: {{ coupon.* }}
            first_coupon = coupons[0] if coupons else None

            for user in users:
                ctx = {
                    "user": user,
                    "coupon": first_coupon,   # convenience
                    "coupons": coupons,       # list (looping)
                }

                if template:
                    subject = _render(template.subject, ctx)
                    html_body = _render(template.body_html, ctx)
                    text_body = _render(template.body_text or "", ctx)
                else:
                    subject = "🎁 Special Discount Coupons Just for You!"
                    coupon_list = "\n".join(
                        [f"- {c.name} ({c.code}) — Expires {c.expiry_date}" for c in coupons]
                    )
                    text_body = (
                        "Hello!\n\nYou have received special discount coupons:\n\n"
                        f"{coupon_list}\n\nEnjoy your shopping!\n— Your Company Team"
                    )
                    html_body = (
                        "<p>Hello!</p><p>You have received special discount coupons:</p>"
                        f"<ul>{''.join([f'<li>{c.name} ({c.code}) — Expires {c.expiry_date}</li>' for c in coupons])}</ul>"
                        "<p>Enjoy your shopping!<br>— Your Company Team</p>"
                    )

                msg = EmailMultiAlternatives(subject, text_body, from_email, [user.email], connection=conn)
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=True)

    t = threading.Thread(target=_task, daemon=True)
    t.start()
    return t
