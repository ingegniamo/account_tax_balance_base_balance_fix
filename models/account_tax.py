from odoo import api, fields, models
from odoo.addons.l10n_it_account.models.account_tax import AccountTax

def _compute_totals_tax(self, data):
        """
        Args:
            data: date range, journals and registry_type
        Returns:
            A tuple: (tax_name, base, tax, deductible, undeductible)

        """
        self.ensure_one()
        context = {
            "from_date": data["from_date"],
            "to_date": data["to_date"],
        }
        registry_type = data.get("registry_type", "customer")
        if data.get("journal_ids"):
            context["vat_registry_journal_ids"] = data["journal_ids"]

        tax = self.env["account.tax"].with_context(**context).browse(self.id)
        tax_name = tax._get_tax_name()
        if not tax.children_tax_ids:
            base_balance = tax.base_balance
            balance = tax.balance
            deductible_balance = tax.deductible_balance
            undeductible_balance = tax.undeductible_balance
            if registry_type == "supplier":
                base_balance = -base_balance
                balance = -balance
                deductible_balance = -deductible_balance
                undeductible_balance = -undeductible_balance
            return (
                tax_name,
                base_balance,
                balance,
                deductible_balance,
                undeductible_balance,
            )
        else:
            # TODO remove?
            base_balance = tax.base_balance

            tax_balance = 0
            deductible = 0
            undeductible = 0
            for child in tax.children_tax_ids:
                child_balance = child.balance
                if (
                    data["registry_type"] == "customer" and child.cee_type == "sale"
                ) or (
                    data["registry_type"] == "supplier" and child.cee_type == "purchase"
                ):
                    # Prendo la parte di competenza di ogni registro e lo
                    # sommo sempre
                    child_balance = child_balance

                elif child.cee_type:
                    continue

                tax_balance += child_balance
                base_balance +=child.base_balance
                account_ids = (
                    child.mapped("invoice_repartition_line_ids.account_id")
                    | child.mapped("refund_repartition_line_ids.account_id")
                ).ids
                if account_ids:
                    deductible += child_balance
                else:
                    undeductible += child_balance
            if registry_type == "supplier":
                base_balance = -base_balance
                tax_balance = -tax_balance
                deductible = -deductible
                undeductible = -undeductible
            return (tax_name, base_balance, tax_balance, deductible, undeductible)
        

AccountTax._compute_totals_tax = _compute_totals_tax