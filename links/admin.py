import io
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.contrib import admin, messages
from django.db.models import Count, Max, Min
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.utils import timezone

import matplotlib
matplotlib.use("Agg")
from matplotlib import dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import patches

from .models import Link, LinkCategory, LinkClick

from tenants.models import Tenant, TenantDomain

PDF_BG_COLOR = "#f8fafc"
PDF_HEADER_COLOR = "#1f2937"
PDF_ACCENT_BLUE = "#2563eb"
PDF_ACCENT_GREEN = "#10b981"
PDF_TEXT_MUTED = "#6b7280"

class TenantFilter(admin.SimpleListFilter):
    title = "tenant"
    parameter_name = "tenant"

    def lookups(self, request, model_admin):
        return list(Tenant.objects.values_list("id", "name"))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(link__domain__tenant_id=self.value())
        return queryset

def export_links_pdf(modeladmin, request, queryset):
    links = queryset.select_related("domain__tenant")

    tz = ZoneInfo("America/Sao_Paulo")
    now = timezone.localtime(timezone.now(), tz)
    clicks_by_day = (
        LinkClick.objects.filter(link__in=links)
        .annotate(day=TruncDate("timestamp", tzinfo=tz))
        .values("link_id", "day")
        .annotate(total=Count("id"))
        .order_by("link_id", "day")
    )
    totals = (
        LinkClick.objects.filter(link__in=links)
        .values("link_id")
        .annotate(
            total=Count("id"),
            first_click=Min("timestamp"),
            last_click=Max("timestamp"),
        )
    )

    counts_by_link = {}
    for row in clicks_by_day:
        counts_by_link.setdefault(row["link_id"], {})[row["day"]] = row["total"]

    totals_by_link = {row["link_id"]: row["total"] for row in totals}
    first_click_by_link = {row["link_id"]: row["first_click"] for row in totals}
    last_click_by_link = {row["link_id"]: row["last_click"] for row in totals}

    buffer = io.BytesIO()
    plt.style.use("seaborn-v0_8-whitegrid")

    with PdfPages(buffer) as pdf:
        for link in links:
            fig = plt.figure(figsize=(8.27, 11.69))  
            gs = fig.add_gridspec(3, 1, height_ratios=[1.1, 0.1, 2.2])

            ax_text = fig.add_subplot(gs[0])
            ax_text.axis("off")

            tenant = getattr(link.domain, "tenant", None) if link.domain_id else None
            tenant_name = tenant.name if tenant else "N/A"
            domain_name = link.domain.domain if link.domain_id else "N/A"
            total_clicks = totals_by_link.get(link.id, 0)
            first_click = first_click_by_link.get(link.id)
            last_click = last_click_by_link.get(link.id)
            last_click_str = (
                timezone.localtime(last_click, tz).strftime("%d/%m/%Y %H:%M")
                if last_click
                else "Sem clicks"
            )
            if first_click and last_click:
                start_date = timezone.localtime(first_click, tz).date()
                end_date = timezone.localtime(last_click, tz).date()
                period_str = f"{start_date:%d/%m/%Y} a {end_date:%d/%m/%Y}"
                date_list = [
                    start_date + timedelta(days=offset)
                    for offset in range((end_date - start_date).days + 1)
                ]
            else:
                period_str = "Sem clicks"
                date_list = []

            lines = [
                "Relatorio de clicks",
                f"Link: {link.name}",
                f"URL: {link.url}",
                f"Tenant: {tenant_name}",
                f"Dominio: {domain_name}",
                f"Ativo: {'Sim' if link.is_active else 'Nao'}",
                f"Total de clicks (todos os tempos): {total_clicks}",
                f"Ultimo click: {last_click_str}",
                f"Periodo do grafico: {period_str}",
            ]

            y = 0.95
            for idx, line in enumerate(lines):
                size = 16 if idx == 0 else 11
                weight = "bold" if idx == 0 else "normal"
                ax_text.text(0, y, line, fontsize=size, fontweight=weight, va="top")
                y -= 0.1 if idx == 0 else 0.08

            ax_chart = fig.add_subplot(gs[2])
            if date_list:
                counts = [counts_by_link.get(link.id, {}).get(day, 0) for day in date_list]
                ax_chart.bar(date_list, counts, color="#1f77b4", width=0.8)
            else:
                ax_chart.text(
                    0.5,
                    0.5,
                    "Sem clicks",
                    ha="center",
                    va="center",
                    color="#6b7280",
                    transform=ax_chart.transAxes,
                )
            ax_chart.set_title("Clicks por dia", fontsize=12, pad=12)
            ax_chart.set_xlabel("Dia")
            ax_chart.set_ylabel("Clicks")

            ax_chart.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=8))
            ax_chart.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
            fig.autofmt_xdate(rotation=30, ha="right")

            fig.text(
                0.5,
                0.02,
                f"Gerado em {now:%d/%m/%Y %H:%M}",
                ha="center",
                fontsize=8,
                color="#666666",
            )

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    filename = f"links_clicks_{now:%Y%m%d_%H%M}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

export_links_pdf.short_description = "Exportar PDF"

def export_linkclicks_pdf(modeladmin, request, queryset):
    clicks = queryset.select_related("link__domain__tenant").order_by("-timestamp")

    def clip(value, limit=60):
        if value is None:
            return ""
        text = str(value)
        if len(text) <= limit:
            return text
        return text[: max(limit - 3, 0)] + "..."

    tz = ZoneInfo("America/Sao_Paulo")
    now = timezone.localtime(timezone.now(), tz)
    total_count = clicks.count()
    first_click = clicks.order_by("timestamp").first()
    last_click = clicks.first()
    period_start = timezone.localtime(first_click.timestamp, tz).date() if first_click else None
    period_end = timezone.localtime(last_click.timestamp, tz).date() if last_click else None

    clicks_by_day = (
        clicks.annotate(day=TruncDate("timestamp", tzinfo=tz))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    top_links = (
        clicks.values("link__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )[:5]

    buffer = io.BytesIO()
    plt.style.use("seaborn-v0_8-whitegrid")

    with PdfPages(buffer) as pdf:
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor(PDF_BG_COLOR)
        gs = fig.add_gridspec(
            3,
            2,
            height_ratios=[0.2, 0.6, 0.2],
            left=0.05,
            right=0.95,
            top=0.95,
            bottom=0.07,
            wspace=0.12,
            hspace=0.2,
        )

        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis("off")
        ax_title.add_patch(
            patches.Rectangle(
                (0, 0.1),
                1,
                0.8,
                transform=ax_title.transAxes,
                facecolor=PDF_HEADER_COLOR,
                edgecolor="none",
            )
        )
        ax_title.text(
            0.03,
            0.6,
            "Relatório de clicks",
            fontsize=18,
            fontweight="bold",
            color="white",
            va="center",
            ha="left",
        )
        ax_title.text(
            0.03,
            0.28,
            f"Gerado em {now:%d/%m/%Y %H:%M}",
            fontsize=10,
            color="#e5e7eb",
            va="center",
            ha="left",
        )
        ax_title.text(
            0.97,
            0.28,
            f"Total: {total_count} clicks",
            fontsize=10,
            color="#e5e7eb",
            va="center",
            ha="right",
        )

        ax_daily = fig.add_subplot(gs[1, 0])
        ax_daily.set_facecolor("white")
        days = [row["day"] for row in clicks_by_day]
        totals = [row["total"] for row in clicks_by_day]
        if days:
            ax_daily.plot(days, totals, color=PDF_ACCENT_BLUE, linewidth=2.5, marker="o", markersize=4)
            ax_daily.fill_between(days, totals, color="#93c5fd", alpha=0.35)
        else:
            ax_daily.text(
                0.5,
                0.5,
                "Sem dados no periodo",
                ha="center",
                va="center",
                color="#6b7280",
                transform=ax_daily.transAxes,
            )
        ax_daily.set_title("Clicks por dia", fontsize=12, pad=10)
        ax_daily.set_xlabel("Dia")
        ax_daily.set_ylabel("Clicks")
        ax_daily.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=8))
        ax_daily.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        for label in ax_daily.get_xticklabels():
            label.set_rotation(30)
            label.set_ha("right")
        ax_daily.set_ylim(bottom=0)
        ax_daily.grid(True, axis="y", color="#e5e7eb")
        ax_daily.grid(False, axis="x")
        ax_daily.spines["top"].set_visible(False)
        ax_daily.spines["right"].set_visible(False)

        ax_top = fig.add_subplot(gs[1, 1])
        ax_top.set_facecolor("white")
        top_names = [clip(row["link__name"] or "N/A", 25) for row in top_links]
        top_totals = [row["total"] for row in top_links]
        if top_names:
            ax_top.barh(top_names[::-1], top_totals[::-1], color=PDF_ACCENT_GREEN, alpha=0.9)
            for i, value in enumerate(top_totals[::-1]):
                ax_top.text(
                    value + 0.05,
                    i,
                    str(value),
                    va="center",
                    fontsize=9,
                    color="#065f46",
                )
        else:
            ax_top.text(
                0.5,
                0.5,
                "Sem dados no periodo",
                ha="center",
                va="center",
                color="#6b7280",
                transform=ax_top.transAxes,
            )
        ax_top.set_title("Top 5 links por clicks", fontsize=12, pad=10)
        ax_top.set_xlabel("Clicks")
        ax_top.set_ylabel("")
        ax_top.grid(True, axis="x", color="#e5e7eb")
        ax_top.grid(False, axis="y")
        ax_top.spines["top"].set_visible(False)
        ax_top.spines["right"].set_visible(False)

        ax_stats = fig.add_subplot(gs[2, :])
        ax_stats.axis("off")
        period_text = (
            f"{period_start:%d/%m/%Y} a {period_end:%d/%m/%Y}"
            if period_start and period_end
            else "Sem dados"
        )

        cards = [
            ("Total de clicks", str(total_count)),
            ("Periodo analisado", period_text),
        ]
        card_width = 0.45
        spacing = 0.04
        x_positions = [0.02, 0.02 + card_width + spacing]
        for idx, (label, value) in enumerate(cards):
            ax_stats.add_patch(
                patches.FancyBboxPatch(
                    (x_positions[idx], 0.1),
                    card_width,
                    0.8,
                    boxstyle="round,pad=0.02,rounding_size=0.02",
                    transform=ax_stats.transAxes,
                    facecolor="white",
                    edgecolor="#e5e7eb",
                    linewidth=1,
                )
            )
            ax_stats.text(
                x_positions[idx] + 0.03,
                0.7,
                label,
                fontsize=9,
                color=PDF_TEXT_MUTED,
                transform=ax_stats.transAxes,
            )
            ax_stats.text(
                x_positions[idx] + 0.03,
                0.35,
                value,
                fontsize=13,
                fontweight="bold",
                color="#111827",
                transform=ax_stats.transAxes,
            )

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    filename = f"linkclicks_{now:%Y%m%d_%H%M}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


export_linkclicks_pdf.short_description = "Exportar Estatísticas"

@admin.register(Link)
class LinksAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "is_active"]
    search_fields = ["name", "url"]
    actions = [export_links_pdf]

    def get_queryset(self, request):
        return Link.all_objects.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "domain":
            kwargs["queryset"] = TenantDomain.objects.exclude(domain="localhost")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(LinkCategory)
class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(LinkClick)
class LinkClickAdmin(admin.ModelAdmin):
    list_display = ["short_id", "link", "timestamp", "referrer", "ip_address"]
    actions = [export_linkclicks_pdf]
    list_filter = ["timestamp", "link", TenantFilter]
    search_fields = ["link__name", "referrer", "user_agent", "payload"]
    readonly_fields = [
        "id",
        "link",
        "timestamp",
        "referrer",
        "ip_address",
        "user_agent",
        "client_x",
        "client_y",
        "viewport_width",
        "viewport_height",
        "payload",
    ]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        (None, {"fields": ("id", "link", "timestamp")}),
        ("Client", {"fields": ("ip_address", "referrer", "user_agent")}),
        ("Coordinates", {"fields": ("client_x", "client_y", "viewport_width", "viewport_height")}),
        ("Payload", {"fields": ("payload",)}),
    )

    def short_id(self, obj):
        return str(obj.id)[:8]

    short_id.admin_order_field = "id"
    short_id.short_description = "ID"
