from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from devis_batiment.models import MaterialLine, QuoteEstimate, QuoteInput
from devis_batiment.services.billing import compute_totals


def _fmt(amount: float, currency: str) -> str:
    return f"{amount:,.0f} {currency}".replace(",", " ")


def build_billing_lines(
    company_info: dict[str, str],
    base_amount: float,
) -> list[tuple[str, str]]:
    """Construit les lignes du bloc totaux (HT/TVA/TTC ou Total, + acompte).

    Le montant estimé est traité comme HT. Renvoie une liste (libellé, valeur).
    """
    currency = company_info.get("currency", "Ar")
    totals = compute_totals(
        base_amount,
        vat_enabled=company_info.get("vat_enabled", "false") == "true",
        vat_rate_pct=float(company_info.get("vat_rate_pct", "20") or 0),
        deposit_pct=float(company_info.get("deposit_pct", "0") or 0),
    )
    lines: list[tuple[str, str]] = []
    if totals.vat_enabled:
        lines.append(("Total HT", _fmt(totals.total_ht, currency)))
        lines.append(
            (f"TVA ({totals.vat_rate_pct:g} %)", _fmt(totals.vat_amount, currency))
        )
        lines.append(("Total TTC", _fmt(totals.total_ttc, currency)))
    else:
        lines.append(("Total", _fmt(totals.total_ht, currency)))
    if totals.deposit_amount > 0:
        lines.append(
            (
                f"Acompte à la commande ({totals.deposit_pct:g} %)",
                _fmt(totals.deposit_amount, currency),
            )
        )
    return lines


def export_quote_pdf(
    output_path: Path,
    company_info: dict[str, str],
    quote_id: int,
    quote_input: QuoteInput,
    estimate: QuoteEstimate,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    title_style = ParagraphStyle(
        name="Title",
        fontSize=18,
        leading=22,
        spaceAfter=8,
        alignment=1,
    )
    heading_style = ParagraphStyle(name="Heading", fontSize=12, leading=14, spaceAfter=6)
    normal_style = ParagraphStyle(name="Normal", fontSize=10, leading=13)
    small_style = ParagraphStyle(name="Small", fontSize=8, leading=10, textColor=colors.HexColor("#64748B"))
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])

    elements = []

    # Logo + titre
    logo_path = company_info.get("company_logo", "")
    if logo_path and Path(logo_path).exists():
        img = Image(logo_path, width=60 * mm, height=20 * mm)
        img.hAlign = "LEFT"
        elements.append(img)
        elements.append(Spacer(1, 4))

    elements.append(Paragraph(company_info.get("company_name", "Jeannot Devis Bâtiment"), title_style))
    company_details = "<br/>".join(
        filter(None, [
            company_info.get("company_address", ""),
            company_info.get("company_phone", ""),
            company_info.get("company_email", ""),
        ])
    )
    if company_details:
        elements.append(Paragraph(company_details, normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"DEVIS N° {quote_id}", heading_style))
    elements.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", normal_style))
    validity = company_info.get("quote_validity_days", "30")
    elements.append(Paragraph(f"Validité : {validity} jours", normal_style))
    elements.append(Spacer(1, 8))

    # Infos client
    client_info = [
        ["Client", quote_input.client_name],
        ["Contact", quote_input.client_contact or "—"],
        ["Projet", quote_input.project_name or quote_input.project_type],
        ["Type de chantier", quote_input.project_type],
        ["Localisation", quote_input.location],
    ]
    if quote_input.surface_m2 > 0:
        client_info.append(["Surface", f"{quote_input.surface_m2:.1f} m²"])
    if estimate.volume_m3 > 0:
        client_info.append(["Volume", f"{estimate.volume_m3:.2f} m³"])

    client_table = Table(client_info, hAlign="LEFT", colWidths=[85 * mm, 85 * mm])
    client_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")] + table_style._cmds))
    elements.append(client_table)
    elements.append(Spacer(1, 12))

    # Tableau des matériaux
    lines = [["Matériau", "Quantité", "Unité", "Prix unitaire", "Total"]]
    for material in estimate.materials:
        lines.append([
            material.name,
            f"{material.quantity:.2f}",
            material.unit,
            f"{material.unit_price:,.0f} {company_info.get('currency', 'Ar')}".replace(",", " "),
            f"{material.line_total:,.0f} {company_info.get('currency', 'Ar')}".replace(",", " "),
        ])
    materials_table = Table(lines, hAlign="LEFT", colWidths=[70 * mm, 25 * mm, 25 * mm, 40 * mm, 40 * mm])
    materials_table.setStyle(table_style)
    elements.append(materials_table)
    elements.append(Spacer(1, 12))

    # Totaux (HT / TVA / TTC ou Total, + acompte éventuel)
    totals = [list(row) for row in build_billing_lines(company_info, estimate.total_amount)]
    totals_table = Table(totals, hAlign="RIGHT", colWidths=[80 * mm, 60 * mm])
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
    ]))
    elements.append(totals_table)
    if company_info.get("vat_enabled", "false") != "true":
        elements.append(Spacer(1, 2))
        elements.append(Paragraph("TVA non applicable.", small_style))
    elements.append(Spacer(1, 16))

    # Mentions : validité, conditions de règlement, conditions générales
    payment_terms = company_info.get("payment_terms", "").strip()
    if payment_terms:
        elements.append(Paragraph("<b>Conditions de règlement :</b>", normal_style))
        elements.append(Paragraph(payment_terms.replace("\n", "<br/>"), normal_style))
        elements.append(Spacer(1, 8))

    terms_conditions = company_info.get("terms_conditions", "").strip()
    if terms_conditions:
        elements.append(Paragraph("<b>Conditions générales :</b>", small_style))
        elements.append(Paragraph(terms_conditions.replace("\n", "<br/>"), small_style))
        elements.append(Spacer(1, 8))

    elements.append(Spacer(1, 8))

    # Signature
    elements.append(Paragraph("Cachet et signature du client :", normal_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Signature : _________________________________", normal_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Fait à .........................., le .......................", normal_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"Document généré par {company_info.get('company_name', 'Jeannot Devis Bâtiment')}",
        small_style,
    ))

    doc.build(elements)
    return output_path
