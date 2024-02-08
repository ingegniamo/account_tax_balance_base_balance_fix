from odoo import _, api, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"
    def get_base_balance_domain(self, state_list, type_list):
        if self.children_tax_ids:
            tax_ids = self.children_tax_ids.ids

            domain = [
                ("move_id.state", "in", state_list),
                ("tax_ids", "in", tax_ids),
            ]
            domain.extend(self.env["account.move.line"]._get_tax_exigible_domain())
            if type_list:
                domain.append(("move_id.financial_type", "in", type_list))
            return domain
        else:
            return super().get_base_balance_domain(state_list, type_list)