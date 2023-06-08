from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    commission_posted = fields.Boolean(string='Commission Posted', default=False)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        journal_id = self.env['account.journal'].search([('name', '=', 'Cash')], limit=1)
        debit_account_id = self.env['account.account'].search([('name', '=', 'Accounts Receivable')], limit=1)
        credit_account_id = self.env['account.account'].search([('name', '=', 'Sales Revenue')], limit=1)

        self.env['account.move'].create({
            'journal_id': journal_id.id,
            'ref': 'Journal Entry #123',
            'line_ids': [(0, 0, {
                'name': 'Debit Line',
                'account_id': debit_account_id.id,
                'debit': 100.0,
                'credit': 0.0,
            }), (0, 0, {
                'name': 'Credit Line',
                'account_id': credit_account_id.id,
                'debit': 0.0,
                'credit': 100.0,
            })],
        })
        # if self.move_type == 'out_invoice' and not self.reversed_entry_id and not self.commission_posted:
        #     print('inside this')
        #     commission_account_id = self.env['account.account'].search(
        #         [('name', '=', 'Commission')]).id  # replace with your commission account
        #     commission_journal_id = self.env['account.journal'].search(
        #         [('name', '=', 'Commission Journal')]).id  # replace with your commission journal
        #     commission_amount = self.amount_total * 0.05  # assuming 5% commission
        #     commission_journal_entry = self.env['account.move'].create({
        #         'journal_id': commission_journal_id,
        #         'ref': self.name,
        #         'move_type': 'entry',
        #         'date': fields.Date.today(),
        #     })
        #     commission_journal_line = {
        #         'name': 'Commission',
        #         'account_id': commission_account_id,
        #         'debit': commission_amount,
        #         'credit': 0.0,
        #         'move_id': commission_journal_entry.id,
        #     }
        #     self.env['account.move.line'].create(commission_journal_line)
        #     commission_journal_line['debit'] = 0.0
        #     commission_journal_line['credit'] = commission_amount
        #     self.env['account.move.line'].create(commission_journal_line)
        #     self.write({'commission_posted': True})
        return res

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
            first_line = move_lines.filtered(lambda line: line.account_id != self.destination_account_id)
            print(self.name_)
            first_line.update({'name_': self.name_})

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

    def write(self, vals):
        if 'name_' in vals:
            # Prevent updating the value of custom_field
            vals.pop('name_')
        return super(AccountInvoiceLineExtraFields, self).write(vals)


