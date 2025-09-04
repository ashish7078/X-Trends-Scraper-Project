import requests
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from .models import TrendRun
# try:
#     from scraper import main as run_scrape
# except Exception:
#     run_scrape = None

@require_GET
def latest_trends(request):
    try:
        t = TrendRun.objects.order_by("-run_timestamp").first()
        if not t:
            return JsonResponse({"error": "No trends found"}, status=404)

        return JsonResponse({
            "unique_id": str(t.id) if t.id else None,
            "trends": [t.trend1, t.trend2, t.trend3, t.trend4, t.trend5],
            "ip_address": t.ip_address,
            "scraped_at": t.run_timestamp.isoformat() if t.run_timestamp else None
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# RENDER_WORKER_URL = os.getenv("RENDER_WORKER_URL")  # e.g. https://my-scraper.onrender.com/trigger-scrape
# RENDER_SECRET_TOKEN = os.getenv("RENDER_SECRET_TOKEN")

# @csrf_exempt
# @require_POST
# def trigger_scrape(request):
#     try:
#         headers = {}
#         if RENDER_SECRET_TOKEN:
#             headers["Authorization"] = f"Bearer {RENDER_SECRET_TOKEN}"

#         # Call Render worker
#         res = requests.post(RENDER_WORKER_URL, headers=headers, timeout=120)
#         res.raise_for_status()
#         data = res.json()

#         return JsonResponse(data)
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)
# @csrf_exempt
# @require_POST
# def scrape_save_trend(request):
#     if run_scrape is None:
#         return JsonResponse({"error": "scraper function not available"}, status=500)
#     try:
#         result = run_scrape() if callable(run_scrape) else None
#         if hasattr(result, "pk") and hasattr(result, "trend1"):
#             obj = result
#         else:
#             if isinstance(result, (list, tuple)):
#                 trends_list = list(result)
#             else:
#                 trends_list = []
#             while len(trends_list) < 5:
#                 trends_list.append("")
#             client_ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
#             obj = TrendRun.objects.create(
#                 trend1=trends_list[0],
#                 trend2=trends_list[1],
#                 trend3=trends_list[2],
#                 trend4=trends_list[3],
#                 trend5=trends_list[4],
#                 ip_address=client_ip
#             )
#         return JsonResponse({
#             "unique_id": str(obj.id),
#             "trend1": obj.trend1,
#             "trend2": obj.trend2,
#             "trend3": obj.trend3,
#             "trend4": obj.trend4,
#             "trend5": obj.trend5,
#             "ip_address": obj.ip_address,
#             "scraped_at": obj.run_timestamp.isoformat()
#         }, status=201)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
