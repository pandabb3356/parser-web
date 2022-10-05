from web import db, sqltype


class TronClassToggle(db.Model):
    __tablename__ = 'tronclass_toggle'

    id = db.Column(db.Integer, primary_key=True)
    feature_toggle_name = db.Column(db.Unicode(255), nullable=False, unique=True)
    description = db.Column(db.Unicode(200))
    default_value = db.Column(db.Boolean, default=False)
