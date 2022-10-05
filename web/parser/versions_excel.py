import pandas as pd

from web.models.service import Service, ServiceType


def prepare_orgs_versions_dfs(record):
    services = Service.query.filter(Service.type == ServiceType.TC).all()

    contents = [
        [
            record_data.org.name
        ]
        +
        [
            record_data.data.get(service.key, '')
            for service in services
        ]
        for record_data in record.record_data_rows
        if record_data.org and record_data.data
    ]

    columns_names = ["org_name"] + list([service.name for service in services])
    df = pd.DataFrame(contents, columns=columns_names)

    df = df.set_index('org_name')
    df_t = df.transpose()

    df.index.name = ''
    df.reset_index(drop=True)

    df_t.reset_index(drop=True)
    df_t.index.name = ''

    return [
        (df, 'service versions version1'),
        (df_t, 'service versions version2')
    ]
