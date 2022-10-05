from flask import request
from flask_restful import marshal
from wtforms import StringField, validators, BooleanField, ValidationError, IntegerField

from web import db
from web.api import bp
from web.api.resource_fields import org_fields
from web.api.response_helper import (
    bad_request_error,
    validation_failed,
    creation_success,
    success,
)
from web.form import BaseForm
from web.models.org import Org


class EditOrgForm(BaseForm):
    org_id = 0

    org_name = StringField(validators=[validators.data_required()])
    org_code = StringField(validators=[validators.data_required()])
    org_protocol = StringField(validators=[validators.data_required()])
    org_domain = StringField(validators=[validators.data_required()])
    is_public_cloud = BooleanField(default=False)
    tc_default_org_id = IntegerField(default=1)

    @classmethod
    def from_request_with(cls, _request, org_id=0):
        form = cls.from_request(_request)
        form.org_id = org_id
        return form

    def validate_org_protocol(self, field):
        if field.data not in ["http", "https"]:
            raise ValidationError("Not a valid protocol!")

    def validate_org_code(self, field):
        org = Org.query.filter(Org.code == field.data).first()
        if (not self.org_id and org is not None) or (self.org_id and org is not None and self.org_id != org.id):
            raise ValidationError(f'This org code is already used by {org.name}!')

    def to_org(self):
        org = Org(
            name=self.org_name.data,
            code=self.org_code.data,
            protocol=self.org_protocol.data,
            domain=self.org_domain.data,
            public_cloud=self.is_public_cloud.data,
            tc_default_org_id=self.tc_default_org_id.data,
        )

        db.session.add(org)

    def update_org(self, org):
        org.code = self.org_code.data
        org.name = self.org_name.data
        org.protocol = self.org_protocol.data
        org.domain = self.org_domain.data
        org.public_cloud = self.is_public_cloud.data
        org.tc_default_org_id = self.tc_default_org_id.data


@bp.route("/orgs/add-org", methods=["POST"])
def add_new_org():
    org_form = EditOrgForm.from_request(request)
    if not org_form.validate():
        return validation_failed(org_form.errors)

    org_form.to_org()
    db.session.commit()

    return creation_success()


@bp.route("/orgs", methods=["GET"])
def get_orgs():
    orgs = Org.query.order_by(Org.id.asc()).all()
    return success({"orgs": marshal(orgs, org_fields)})


@bp.route("/orgs/<int:org_id>", methods=["GET"])
def get_org(org_id):
    org = Org.query.get_or_404(org_id)
    return success({"org": marshal(org, org_fields)})


@bp.route("/orgs/<int:org_id>", methods=["PUT"])
def update_org(org_id):
    org = Org.query.get_or_404(org_id)
    org_form = EditOrgForm.from_request_with(request, org_id=org_id)
    if not org_form.validate():
        return validation_failed(org_form.errors)

    org_form.update_org(org)
    db.session.commit()
    return success()


@bp.route("/orgs/<int:org_id>", methods=["DELETE"])
def delete_org(org_id):
    org = Org.query.filter(Org.id == org_id).first()
    if org is None:
        return bad_request_error()

    db.session.delete(org)
    db.session.commit()
    return success()
