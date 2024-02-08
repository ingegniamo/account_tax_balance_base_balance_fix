from odoo import _, api, fields, models
from odoo.addons.account_tax_balance.models.account_tax import AccountTax
import logging
_logger = logging.getLogger(__name__)

get_balance_domain_orig= AccountTax.get_balance_domain
get_base_balance_domain_orig= AccountTax.get_base_balance_domain
def get_balance_domain(self, state_list, type_list):
    if self.children_tax_ids and not self.env.context.get("no_balance_children", False):
        tax_ids = self.children_tax_ids.ids
        domain = [
            ("move_id.state", "in", state_list),
            ("tax_line_id", "in", tax_ids),
        ]
        domain.extend(self.env["account.move.line"]._get_tax_exigible_domain())
        if type_list:
            domain.append(("move_id.financial_type", "in", type_list))
        return domain
    else:
        return get_balance_domain_orig(self, state_list, type_list)
    
def get_base_balance_domain(self, state_list, type_list):
    if self.children_tax_ids and not self.env.context.get("no_balance_children", False):
        tax_ids = self.children_tax_ids.ids

        domain = [
            ("move_id.state", "in", state_list),
            ("tax_ids", "in", tax_ids),
        ]
        domain.extend(self.env["account.move.line"]._get_tax_exigible_domain())
        if type_list:
            domain.append(("move_id.financial_type", "in", type_list))
        _logger.info(domain)
        return domain
    else:
        return get_base_balance_domain_orig(self, state_list, type_list)

AccountTax.get_balance_domain = get_balance_domain
AccountTax.get_base_balance_domain = get_base_balance_domain
