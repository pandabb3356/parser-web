<template>
    <CCard>
        <CProgress showPercentage :color="completenessColor" v-if="currentRecord" :value="parseInt(currentRecord.completeness)"></CProgress>
        <CCardHeader>
          <CIcon name="cil-justify-center"/><strong> Toggles</strong>
        </CCardHeader>
        <CCardBody>
            <CRow class="align-items-center">
                <CButton color="success" class="version-button" @click="transpose">
                    <CIcon style="width: 0;" />
                    <strong>Transpose Table</strong>
                </CButton>
                <CButton color="primary" class="version-button" @click="downloadExcel">
                    <CIcon name="cil-cloud-download" />&nbsp;<strong>Export Excel</strong>
                </CButton>
            </CRow>
            <br/>
            <div v-if="ui.contentLoadingComplete && currentTableId === versionsTableId.VERSION1">
                <table :id="versionsTableId.VERSION1" class="table table-striped table-bordered" v-if="toggles.length > 0">
                    <thead>
                    <tr>
                        <th>Idx</th>
                        <th>Toggle Description</th>
                        <th>Toggle Name</th>
                        <th>Toggle Default Value</th>
                        <th v-for="data in recordData">
                            <span v-if="hasErrorRecord(data)" :id="getErrorRecordId(data)">
                                <i data-toggle="tooltip"
                                   :title="getErrorRecord(data)"
                                   class="fas fa-exclamation-triangle text-danger">
                                </i>
                            </span>
                            <span>
                              <CBadge class="org-label" color="success">{{data.org.code}}</CBadge>
                              <br/>
                              {{data.org.name}}
                            </span>
                        </th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="(toggle, tIdx) in toggles">
                        <td>{{ tIdx + 1 }}</td>
                        <td>{{ toggle && toggle.description }}</td>
                        <td>{{ toggle.feature_toggle_name }}</td>
                        <td>{{ getToggleDefaultValue(toggle) }}</td>
                        <td v-for="data in recordData">
                        <span v-if="hasToggleValue(data, toggle.feature_toggle_name)">
                            {{ getToggleValue(data, toggle.feature_toggle_name) }}
                        </span>
                            <span v-else>&nbsp;</span>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
            <div v-else-if="ui.contentLoadingComplete && currentTableId === versionsTableId.VERSION2">
                <table :id="versionsTableId.VERSION2" class="table table-striped table-bordered" v-if="toggles.length > 0">
                    <thead>
                    <tr>
                        <th>Idx</th>
                        <th>Org</th>
                        <th v-for="(toggle, tIdx) in toggles">
                            <span>{{ toggle.feature_toggle_name }}</span>
                        </th>
                    </tr>
                    </thead>

                    <tbody>
                    <tr v-for="(data, dIdx) in recordData">
                        <td>{{ dIdx + 1 }}</td>
                        <td>
                        <span v-if="hasErrorRecord(data)" :id="getErrorRecordId(data)">
                            <i data-toggle="tooltip" :data-target="getErrorRecordId(data)"
                               :title="getErrorRecord(data)"
                               class="fas fa-exclamation-triangle text-danger"
                               :aria-describedby="getErrorRecordId(data)">
                            </i>
                        </span>
                            <span>
                          <CBadge class="org-label" color="success">{{data.org.code}}</CBadge>
                          <br/>
                          {{data.org.name}}
                        </span>
                        </td>
                        <td v-for="toggle in toggles">
                        <span v-if="hasToggleValue(data, toggle.feature_toggle_name)">
                            {{ getToggleValue(data, toggle.feature_toggle_name) }}
                        </span>
                            <span v-else>&nbsp;</span>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </CCardBody>
    </CCard>
</template>

<script type="text/jsx">
    import 'datatables.net-dt/js/dataTables.dataTables'
    import 'datatables.net-fixedcolumns-dt/js/fixedColumns.dataTables'
    import 'datatables.net-fixedheader-dt/js/fixedHeader.dataTables'

    import 'datatables.net-bs4/css/dataTables.bootstrap4.min.css'
    import 'datatables.net-fixedcolumns-bs4/css/fixedColumns.bootstrap4.min.css'
    import 'datatables.net-fixedheader-dt/css/fixedHeader.dataTables.min.css'
    import 'datatables.net-fixedheader-bs4/css/fixedHeader.bootstrap4.min.css'

    const versionsTableId = {
        VERSION1: 'VersionsTable1',
        VERSION2: 'VersionsTable2',
    }

    const queryInterval = 1000;

    String.prototype.capitalize = function() {
        return this.charAt(0).toUpperCase() + this.slice(1);
    }

    export default {
        name: "OrgToggles",
        data() {
            return {
                currentRecord: null,
                records: [],
                recordData: [],
                ui: {
                    contentLoadingComplete: false
                },
                intervalRecordCheck: null,
                recordStatus: {
                    PROCESSING: 'processing',
                    FINISHED: 'finished',
                    FAILED: 'failed',
                },
                toggles: [],
                currentTableId: versionsTableId.VERSION1,
                versionsTableId: versionsTableId,
            }
        },
        computed: {
            completenessColor() {
              const completeness = parseInt(this.currentRecord.completeness);
              switch (completeness) {
                  case 100:
                      return "success"
                  default: return "warning"
              }
            },
            recordId() {
              return this.$route.params.id
            },
            tableData() {
                const self = this;
                let data = [];
                if (this.currentTableId === versionsTableId.VERSION2) {
                    data = self.recordData.map(rd => {
                        let rowData = {
                            org: rd.org
                        };

                        rowData = Object.assign(rowData, rd.data)

                        return rowData
                    });
                } else {
                    const serviceMap = this.initServiceMap();

                    self.recordData.forEach(rd => {
                        for (let service of self.services) {
                            serviceMap[service.key][`org_${rd.org.id}_service`] = {
                                id: rd.org.id,
                                code: rd.org,
                                name: rd.org.name,
                                version: rd.data[service.key],

                            }
                        }
                    });

                    for (let service of this.services) {
                        const row = serviceMap[service.key] || {};
                        row["service_name"] = service.name
                        data = data.concat([row]);
                    }
                }

                return data
            },
            fixedColumnsCount() {
                return this.currentTableId === this.versionsTableId.VERSION1 ? 4 : 2
            }
        },
        methods: {
            initTable() {
                let self = this;

                if (this.currentRecord && this.currentRecord.status === this.recordStatus.FINISHED) {
                    setTimeout(function () {
                        $(`#${self.currentTableId}`).DataTable({
                            scrollX: true,
                            paging: false,
                            fixedHeader: {
                                header: true,
                                footer: true
                            },
                            fixedColumns: {
                                leftColumns: self.fixedColumnsCount,
                            },
                            scrollY: "400px",
                        });

                        // $('[data-toggle="tooltip"]').tooltip();
                    });
                }
            },
            init() {
                let self = this;

                self.getRecordData().then(function (response) {
                    self.currentRecord = response.data.record;
                    if (self.currentRecord.status === self.recordStatus.PROCESSING) {
                        self.intervalRecordCheck = setInterval(self.getSyncRecordStatus, queryInterval);
                    }
                    self.recordData = response.data.record_data_rows || [];
                    self.toggles = response.data.toggles || [];
                    self.ui.contentLoadingComplete = true;
                    self.initTable();
                }).catch()
            },
            getRecords() {
                const recordType = 'toggle';
                const url = `/api/parser/${recordType}/records`;
                return this.$http.get(url)
            },
            getRecordData() {
                const url = `/api/parser/toggles-parser/records/${this.recordId}/record-data`;
                return this.$http.get(url)
            },
            getSyncRecordStatus() {
                let self = this;

                const url = `/api/parser/toggles-parser/records/${this.recordId}/record-data`;
                this.$http.get(url).then(function (response) {
                    self.currentRecord = response.data.record;
                    self.recordData = response.data.record_data_rows || [];
                    if (self.intervalRecordCheck !== null && self.currentRecord.status === self.recordStatus.FINISHED) {
                        clearInterval(self.intervalRecordCheck)
                    }
                    self.initTable();
                }).catch(function () {
                    // window.toastr.error('Some errors are occurred!');
                })
            },
            hasToggleValue (recordData, toggleName) {
                return (recordData && recordData.data).hasOwnProperty(toggleName)
            },
            getToggleValue (recordData, toggleName) {
                if (!recordData || !recordData.data) {
                    return ''
                } else if (recordData.data[toggleName] === true || recordData.data[toggleName] === 'True' || recordData.data[toggleName] === 'true') {
                    return '1'
                } else if (recordData.data[toggleName] === false || recordData.data[toggleName] === 'False' || recordData.data[toggleName] === 'false') {
                    return '0'
                } else {
                    return ''
                }
            },
            getToggleDefaultValue (toggle) {
                if (!toggle || !toggle.hasOwnProperty('default_value')) {
                    return ''
                } else if (toggle.default_value === true) {
                    return '1'
                } else if (toggle.default_value === false) {
                    return '0'
                } else {
                    return ''
                }
            },
            transpose () {
                let self = this;

                this.ui.contentLoadingComplete = false;
                this.currentTableId = this.currentTableId === this.versionsTableId.VERSION2 ? this.versionsTableId.VERSION1 : this.versionsTableId.VERSION2;

                setTimeout(function () {
                   self.ui.contentLoadingComplete = true;
                   self.initTable();
                }, 100);
            },
            deleteRecord (record) {
                if (!record || !window.confirm(`Are you sure to delete this record (${record.id})`)) {
                    return
                }

                let self = this;

                const url = `/api/parser/records/${record.id}`;

                this.$http.delete(url).then(function (response) {
                    // window.toastr.success(`Delete the record (${record.id}) successfully!`);

                    setTimeout(function () {
                        window.location.reload();
                    }, 300)

                }).catch(function () {
                    // window.toastr.error('Some errors are occurred!')
                })

            },
            hasErrorRecord (recordData) {
                return Boolean(recordData && recordData.data && recordData.data["health-check-error"])
            },
            getErrorRecord (recordData) {
                return String(recordData && recordData.data && String(recordData.data["health-check-error"])).substring(0, 20)
            },
            getErrorRecordId (recordData) {
                return `org-${recordData.org_id}-health-check-error`
            },
            downloadExcel () {
                const self = this;
                return this.$http.get(`/api/parser/toggles-parser/records/${this.recordId}/excel`, {
                    responseType: 'blob'
                }).then(
                    (response) => {
                        let blob = new Blob([response.data], {type: response.headers['content-type']})
                        let filename = (response.headers['content-disposition'] || '').split('filename=')[1];
                        const result = document.createElement('a');
                        result.href = window.URL.createObjectURL(blob);
                        result.download = filename;
                        result.click();
                    }
                ).catch((error) => {
                    self.$toast.error('Some errors are occurred!');
                });
            },
            clearIntervalCheck() {
            if (this.intervalRecordCheck) {
                clearInterval(this.intervalRecordCheck);
            }
        },
        },
        mounted: function mounted() {
            this.init();
        },
        destroyed() {
            this.clearIntervalCheck();
        }
    }
</script>

<style scoped type="text/scss">

    .version-button {
        margin-left: 10px;
    }

    .org-label {
        padding: 2px;
    }
</style>