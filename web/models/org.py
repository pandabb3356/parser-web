from web import db


class Org(db.Model):
    __tablename__ = 'org'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255), nullable=False)
    protocol = db.Column(db.Unicode(10), nullable=False)
    domain = db.Column(db.Unicode(255), nullable=False)
    code = db.Column(db.Unicode(100), nullable=False)
    public_cloud = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    tc_default_org_id = db.Column(db.Integer, default=1)

    @property
    def server_address(self):
        return f"{self.protocol}://{self.domain}"
