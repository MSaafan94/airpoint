from odoo import fields, models, api, _


class SaleOrderLineSearch(models.Model):
    _inherit = 'sale.order'

    order_line_name = fields.Char(
        string='Order Line Name',
        compute='_compute_order_line_name',
        search='_search_order_line_name',
    )

    @api.depends('order_line')
    def _compute_order_line_name(self):
        for record in self:
            record.order_line_name = ', '.join(record.mapped('order_line.name_'))

    def _search_order_line_name(self, operator, value):
        order_lines = self.env['sale.order.line'].search([('name_', operator, value)])
        order_ids = order_lines.mapped('order_id').ids
        return [('id', 'in', order_ids)]

    @api.depends('order_line')
    def _compute_order_line_name(self):
        for record in self:
            record.order_line_name = ', '.join(record.mapped('order_line.tkt_no'))

    order_line_tkt_no = fields.Char(
        string='Order Line Ticket No',
        compute='_compute_order_line_tkt_no',
        search='_search_order_line_tkt_no',
    )

    @api.depends('order_line')
    def _compute_order_line_tkt_no(self):
        for record in self:
            record.order_line_tkt_no = ', '.join(record.mapped('order_line.tkt_no'))

    def _search_order_line_tkt_no(self, operator, value):
        order_lines = self.env['sale.order.line'].search([('tkt_no', operator, value)])
        order_ids = order_lines.mapped('order_id').ids
        return [('id', 'in', order_ids)]

    order_line_reference = fields.Char(
        string='Order Line reference',
        compute='_compute_order_line_reference',
        search='_search_order_line_reference',
    )

    @api.depends('order_line')
    def _compute_order_line_reference(self):
        for record in self:
            record.order_line_reference = ', '.join(record.mapped('order_line.reference'))

    def _search_order_line_reference(self, operator, value):
        order_lines = self.env['sale.order.line'].search([('reference', operator, value)])
        order_ids = order_lines.mapped('order_id').ids
        return [('id', 'in', order_ids)]


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_reverse(self):
        action = super(AccountMove, self).action_reverse()

        if self.is_invoice():
            action['name'] = _('Credit Note')

            credit_lines = self.line_ids.filtered(lambda l: l.credit > 0)
            for line in credit_lines:
                origin_line = self.line_ids.filtered(
                    lambda l: l.id == line.move_id.line_ids.filtered(
                        lambda
                            l2: l2.debit > 0 and l2.product_id.id == line.product_id.id and l2.account_id.id == line.account_id.id
                    ).id
                )
                if origin_line:
                    line.name_ = origin_line.name_
                    line.trip_code = origin_line.trip_code
                    line.airline = origin_line.airline
                    line.serial_number = origin_line.serial_number
                    line.route = origin_line.route
                    line.tkt_no = origin_line.tkt_no
                    line.reference = origin_line.reference
                    line.cost = origin_line.cost

        return action


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


class AccountPaymentt(models.Model):
    _inherit = 'account.payment'
    name_ = fields.Char(related='ref', string='hee')

    def action_post(self):
        ''' draft -> posted '''
        res = super(AccountPaymentt, self).action_post()

        if self.name_:
            move = self.move_id
            move_lines = move.line_ids

            # Update the custom 'name_' field for all journal items in the move
            for line in move_lines:
                line.update({'name_': self.name_})

        return res


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