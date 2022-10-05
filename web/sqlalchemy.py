from enum import Enum


class DBType(Enum):
    postgresql = "postgresql"


DB_PREFIX_MAP = {DBType.postgresql.value: "postgresql"}


def get_sqla_database_prefix(db_type):
    return DB_PREFIX_MAP.get(db_type, db_type)


def get_sqla_database_uri(db_user, db_pwd, db_host, db_port, db_database, db_type):
    db_prefix = get_sqla_database_prefix(db_type)

    return f"{db_prefix}://{db_user}{':' + db_pwd if db_pwd else ''}@{db_host}:{db_port}/{db_database}"
