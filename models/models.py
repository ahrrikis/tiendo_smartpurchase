# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

# class tiendo_smartpurchase(models.Model):
#     _name = 'tiendo_smartpurchase.tiendo_smartpurchase'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def make_po(self):
        """
        Correction of make_po method, to avoid price selection of unavailable prices.
        :return: Array of created Purchase Orders.
        """
        self._before_make_po()
        cache = {}
        res = []
        for procurement in self:
            #product_qty
            suppliers = self._get_supplier(procurement)
            if not suppliers:
                procurement.message_post(body=_('No vendor associated to product %s. Please set one to fix this procurement.') % (procurement.product_id.name))
                continue
            supplier = procurement._make_po_select_supplier(suppliers)
            partner = supplier.name

            domain = procurement._make_po_get_domain(partner)

            if domain in cache:
                po = cache[domain]
            else:
                po = self.env['purchase.order'].search([dom for dom in domain])
                po = po[0] if po else False
                cache[domain] = po
            if not po:
                vals = procurement._prepare_purchase_order(partner)
                po = self.env['purchase.order'].create(vals)
                name = (procurement.group_id and (procurement.group_id.name + ":") or "") + (procurement.name != "/" and procurement.name or procurement.move_dest_id.raw_material_production_id and procurement.move_dest_id.raw_material_production_id.name or "")
                message = _("This purchase order has been created from: <a href=# data-oe-model=procurement.order data-oe-id=%d>%s</a>") % (procurement.id, name)
                po.message_post(body=message)
                cache[domain] = po
            elif not po.origin or procurement.origin not in po.origin.split(', '):
                # Keep track of all procurements
                if po.origin:
                    if procurement.origin:
                        po.write({'origin': po.origin + ', ' + procurement.origin})
                    else:
                        po.write({'origin': po.origin})
                else:
                    po.write({'origin': procurement.origin})
                name = (self.group_id and (self.group_id.name + ":") or "") + (self.name != "/" and self.name or self.move_dest_id.raw_material_production_id and self.move_dest_id.raw_material_production_id.name or "")
                message = _("This purchase order has been modified from: <a href=# data-oe-model=procurement.order data-oe-id=%d>%s</a>") % (procurement.id, name)
                po.message_post(body=message)
            if po:
                res += [procurement.id]

            # Create Line
            po_line = False
            for line in po.order_line:
                if line.product_id == procurement.product_id and line.product_uom == procurement.product_id.uom_po_id:
                    procurement_uom_po_qty = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_po_id)
                    seller = procurement.product_id._select_seller(
                        partner_id=partner,
                        quantity=line.product_qty + procurement_uom_po_qty,
                        date=po.date_order and po.date_order[:10],
                        uom_id=procurement.product_id.uom_po_id)

                    price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, line.product_id.supplier_taxes_id, line.taxes_id) if seller else 0.0
                    if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
                        price_unit = seller.currency_id.compute(price_unit, po.currency_id)

                    po_line = line.write({
                        'product_qty': line.product_qty + procurement_uom_po_qty,
                        'price_unit': price_unit,
                        'procurement_ids': [(4, procurement.id)]
                    })
                    break
            if not po_line:
                vals = procurement._prepare_purchase_order_line(po, supplier)
                self.env['purchase.order.line'].create(vals)
        return res

    def _get_supplier(self, procurement):
        """
        Selects the available suppliers from Product.Supplierinfo
        :param procurement: Procurement available supplier shall be given for.
        :return: collection of available suppliers for given procurement
        """
        # Original behavior doesn't take supplier tier price into consideration.
        # suppliers = procurement.product_id.seller_ids \
        #    .filtered(lambda r: (not r.company_id or r.company_id == procurement.company_id) and (
        #not r.product_id or r.product_id == procurement.product_id))
        suppliers = procurement.product_id.seller_ids \
            .filtered(lambda r: (not r.company_id or r.company_id == procurement.company_id) and (
            not r.product_id or r.product_id == procurement.product_id) and (r.min_qty <= procurement.product_qty))
        return suppliers

    def _make_po_select_supplier(self, suppliers):
        """ This method selects the cheapest seller that has a valid price. Tier prices cannot considered here, for
        consideration the suppliers input has to be without prices that are not available for quantities purchased
        in this order.
        """
        date = fields.Date.today()
        supplier = suppliers[0]
        for seller in suppliers:
            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if supplier.price > seller.price:
                supplier = seller
        return supplier

    def _before_make_po(self):
        """Empty method for easier extension of make_po method."""
