import pandas as pd

from web.models.toggle import TronClassToggle


def get_toggle_keys(record, toggles):
    toggle_keys = [toggle.feature_toggle_name for toggle in toggles]

    for record_data in record.record_data_rows:
        data = (record_data.data or {})
        if not isinstance(data, dict) or 'toggles-error' in data:
            continue

        for k, v in data.items():
            if k not in toggle_keys:
                toggle_keys.append(k)

    return toggle_keys


def prepare_orgs_toggles_dfs(record):
    toggles = TronClassToggle.query.order_by(TronClassToggle.id).all()
    toggle_keys = get_toggle_keys(record, toggles)

    def trans_value(value):
        if value is None:
            return ""
        return 1 if value == 'True' or value is True else 0

    contents = [
        [
            record_data.org.name
        ]
        +
        [
            trans_value(record_data.data.get(toggle_key))
            for toggle_key in toggle_keys
        ]
        for record_data in record.record_data_rows
        if record_data.org and record_data.data
    ]
    columns_names = ["org_name"] + list(toggle_keys)

    df = pd.DataFrame(contents, columns=columns_names)

    df = df.set_index('org_name')
    df_t = df.transpose()

    df.index.name = ''
    df.reset_index(drop=True)

    df_t.reset_index(drop=True)
    df_t.index.name = ''

    return [
        (df, 'toggles version1'),
        (df_t, 'toggles version2')
    ]
