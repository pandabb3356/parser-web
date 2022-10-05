from bs4 import BeautifulSoup

from web import db
from web.api_service import TronClassApiService
from web.parser.base_parser import BaseParser


class TogglesParser(BaseParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def parse_toggles(html_text, parse_org_id=1):
        soup = BeautifulSoup(html_text, 'html.parser')

        table_rows = soup.find_all('table', class_="table table-sm table-bordered")
        if not table_rows:
            return

        parse_org_val_idx = 3
        table = table_rows[0]
        thead = table.find('thead')
        tbody = table.find('tbody')
        if not tbody:
            return

        toggle_map = {}

        table_head_row = thead.find_all('tr')
        if table_head_row:
            table_heads = table_head_row[0].find_all('th')
            for hi, head in enumerate(table_heads[3:]):
                span_rows = head.find_all('span')
                if not span_rows:
                    continue

                span = span_rows[0]
                if span.text.isdigit() and int(span.text) == parse_org_id:
                    parse_org_val_idx += hi
                    break

        rows = tbody.find_all('tr')
        toggles_len = 0
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]

            if len(cols) < 2:
                continue

            toggle_name, toggle_default_value = cols[1], cols[2]
            toggle_value = None if parse_org_val_idx >= len(cols) else cols[parse_org_val_idx]

            if not toggle_name:
                continue

            toggles_len += 1

            toggle_map[toggle_name] = toggle_value or toggle_default_value

        return toggle_map

    @classmethod
    def get_toggles_html(cls, org):
        try:
            api_service = TronClassApiService(org_code=org.code, server_url=org.server_address)
            response = api_service.get_toggles(timeout=cls.DEFAULT_TIMEOUT)
            if not response.ok:
                return None, f'Status Code({response.status_code}): {response.text}'
            return response.text, None
        except Exception as ex:
            return None, f'Error: {str(ex)}'

    def fetch_data(self):
        for o_idx, org in enumerate(self.orgs):
            if not org.public_cloud:
                org_toggle_map = {}
                html_text, error = self.get_toggles_html(org=org)
                if html_text:
                    org_toggle_map = self.parse_toggles(html_text, parse_org_id=org.tc_default_org_id or 1)
                    self.finished_orgs += [org]
                else:
                    self.failed_orgs += [(org, error)]
                    org_toggle_map['toggles-error'] = str(error)

                self.add_record_data(data=org_toggle_map, org_id=org.id)

            import time
            time.sleep(1)

            self.update_record_completeness()
            db.session.commit()

        self.record.completeness = 100
        db.session.commit()
