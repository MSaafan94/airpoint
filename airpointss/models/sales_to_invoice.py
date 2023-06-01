from odoo import fields, models, 


class ExtraOrderFields(models.Model):
    _inherit = 'sale.order.line'

    name_ = fields.Char(string='name')
    trip_code = fields.Char()
    airline = fields.Char()
    serial_number = fields.Char()
    route = fields.Char()
    tkt_no = fields.Char()
    reference = fields.Char()
    cost = fields.Char()

    def _prepare_invoice_line(self, **optional_values):

        res = super(ExtraOrderFields, self)._prepare_invoice_line(**optional_values)
        res.update({
            'name_': self.name_,
            'trip_code': self.trip_code,
            'airline': self.airline,
            'serial_number': self.serial_number,
            'route': self.route,
            'tkt_no': self.tkt_no,
            'reference': self.reference,
            'cost': self.cost,
        })
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    # def action_reverse(self):
    #     action = super(AccountMove, self).action_reverse()
    #
    #     if self.is_invoice():
    #         action['name'] = _('Credit Note')
    #
    #         credit_lines = self.line_ids.filtered(lambda l: l.credit > 0)
    #         for line in credit_lines:
    #             origin_line = self.line_ids.filtered(
    #                 lambda l: l.id == line.move_id.line_ids.filtered(
    #                     lambda
    #                         l2: l2.debit > 0 and l2.product_id.id == line.product_id.id and l2.account_id.id == line.account_id.id
    #                 ).id
    #             )
    #             if origin_line:
    #                 line.name_ = origin_line.name_
    #                 line.trip_code = origin_line.trip_code
    #                 line.airline = origin_line.airline
    #                 line.serial_number = origin_line.serial_number
    #                 line.route = origin_line.route
    #                 line.tkt_no = origin_line.tkt_no
    #                 line.reference = origin_line.reference
    #                 line.cost = origin_line.cost
    #
    #     return action


class AccountInvoiceLineExtraFields(models.Model):
    _inherit = "account.move.line"

    name_ = fields.Char()
    trip_code = fields.Char()
    airline = fields.Char()
    serial_number = fields.Char()
    route = fields.Char()
    tkt_no = fields.Char()
    reference = fields.Char()
    cost = fields.Char()