from odoo import api, fields, models , tools
from odoo.tools import float_compare, pycompat

class invoice_design_wc(models.Model):
    _name = 'invoice.design.wc'
    # _rec_name = 'image1'
    _description = 'New Description'


    image1 = fields.Binary(string="image1", attachment=True)
    image2 = fields.Binary(string="image2", )
    image3 = fields.Binary(string="image3", )
    image4 = fields.Binary(string="image4", )
    image5 = fields.Binary(string="image5", )

    @api.one
    def _set_image_small(self):
        self._set_image_value(self.image1)

    @api.one
    def _set_image_value(self, value):
        if isinstance(value, pycompat.text_type):
            value = value.encode('ascii')
        image = tools.image_resize_image_big(value)
        self.image1 = image

class invoice_configuration(models.Model):
    _inherit="account.invoice"
    design_id = fields.Many2one('invoice.design.wc',
                                 string='Company',store=True, readonly=True)
    img1 = fields.Binary(related="design_id.image1",store=True,string="image1", )
    img2 = fields.Binary(related="design_id.image2",string="image2", )
    img3 = fields.Binary(related="design_id.image3",string="image3", )
    img4 = fields.Binary(related="design_id.image4",string="image4", )
    img5 = fields.Binary(related="design_id.image5",string="image5", )
