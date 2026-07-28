from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BillingTotals:
    vat_enabled: bool
    total_ht: float
    vat_rate_pct: float
    vat_amount: float
    total_ttc: float
    deposit_pct: float
    deposit_amount: float


def compute_totals(
    base_amount: float,
    vat_enabled: bool,
    vat_rate_pct: float,
    deposit_pct: float,
) -> BillingTotals:
    """Habillage commercial du montant estimé (traité comme HT).

    Le moteur de calcul reste inchangé : cette fonction ajoute seulement la TVA
    optionnelle et l'acompte au-dessus du total. TVA et acompte s'appliquent au
    TTC (égal au HT quand la TVA est désactivée).
    """
    total_ht = base_amount
    vat_amount = total_ht * (vat_rate_pct / 100.0) if vat_enabled else 0.0
    total_ttc = total_ht + vat_amount
    deposit_amount = total_ttc * (deposit_pct / 100.0)
    return BillingTotals(
        vat_enabled=vat_enabled,
        total_ht=total_ht,
        vat_rate_pct=vat_rate_pct if vat_enabled else 0.0,
        vat_amount=vat_amount,
        total_ttc=total_ttc,
        deposit_pct=deposit_pct,
        deposit_amount=deposit_amount,
    )
