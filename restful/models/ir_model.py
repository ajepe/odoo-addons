# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class IrModel(models.Model):
    """Enable all models to be available for API request."""

    _inherit = "ir.model"

    rest_api = fields.Boolean("REST API", default=True, help="Allow this model to be fetched through REST API")


class IrAttachment(models.Model):
    """docstring for Attachement"""

    _inherit = "ir.attachment"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # add res_field=False in domain if not present; the arg[0] trick below
        # # works for domain items and '&'/'|'/'!' operators too
        # if not any(arg[0] in ('id', 'res_field') for arg in args):
        #     args.insert(0, ('res_field', '=', False))

        ids = super(IrAttachment, self)._search(
            args, offset=offset, limit=limit, order=order, count=False, access_rights_uid=access_rights_uid
        )
        return ids

        if self.env.is_system():
            # rules do not apply for the superuser
            return len(ids) if count else ids

        if not ids:
            return 0 if count else []

        # Work with a set, as list.remove() is prohibitive for large lists of documents
        # (takes 20+ seconds on a db with 100k docs during search_count()!)
        orig_ids = ids
        ids = set(ids)

        # For attachments, the permissions of the document they are attached to
        # apply, so we must remove attachments for which the user cannot access
        # the linked document.
        # Use pure SQL rather than read() as it is about 50% faster for large dbs (100k+ docs),
        # and the permissions are checked in super() and below anyway.
        model_attachments = defaultdict(lambda: defaultdict(set))  # {res_model: {res_id: set(ids)}}
        binary_fields_attachments = set()
        self._cr.execute(
            """SELECT id, res_model, res_id, public, res_field FROM ir_attachment WHERE id IN %s""", [tuple(ids)]
        )
        for row in self._cr.dictfetchall():
            if not row["res_model"] or row["public"]:
                continue
            # model_attachments = {res_model: {res_id: set(ids)}}
            model_attachments[row["res_model"]][row["res_id"]].add(row["id"])
            # Should not retrieve binary fields attachments
            if row["res_field"]:
                binary_fields_attachments.add(row["id"])

        if binary_fields_attachments:
            ids.difference_update(binary_fields_attachments)

        # To avoid multiple queries for each attachment found, checks are
        # performed in batch as much as possible.
        for res_model, targets in model_attachments.items():
            if res_model not in self.env:
                continue
            if not self.env[res_model].check_access_rights("read", False):
                # remove all corresponding attachment ids
                ids.difference_update(itertools.chain(*targets.values()))
                continue
            # filter ids according to what access rules permit
            target_ids = list(targets)
            allowed = self.env[res_model].with_context(active_test=False).search([("id", "in", target_ids)])
            for res_id in set(target_ids).difference(allowed.ids):
                ids.difference_update(targets[res_id])

        # sort result according to the original sort ordering
        result = [id for id in orig_ids if id in ids]

        # If the original search reached the limit, it is important the
        # filtered record set does so too. When a JS view recieve a
        # record set whose length is bellow the limit, it thinks it
        # reached the last page.
        if len(orig_ids) == limit and len(result) < len(orig_ids):
            result.extend(
                self._search(
                    args,
                    offset=offset + len(orig_ids),
                    limit=limit,
                    order=order,
                    count=count,
                    access_rights_uid=access_rights_uid,
                )[: limit - len(result)]
            )

        return len(result) if count else list(result)
