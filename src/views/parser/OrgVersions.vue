<template>
    <CCard>
        <CProgress showPercentage :color="completenessColor" v-if="currentRecord" :value="parseInt(currentRecord.completeness)"></CProgress>
        <CCardHeader>
          <CIcon name="cil-justify-center"/><strong> Versions</strong>
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
            <ve-table v-if="currentRecord" :columns="columns"
                      :table-data="tableData"
                      fixed-header="true"
                      :max-height="500"
                      :row-style-option="rowStyleOption"
            />
        </CCardBody>
    </CCard>
</template>

<script type="text/jsx">
    import Vue from "vue";
    import "vue-easytable/libs/theme-default/index.css"; // import style

    import { VeTable, VePagination, VeIcon, VeLoading } from "vue-easytable";

    Vue.use(VeTable);
    Vue.use(VePagination);
    Vue.use(VeIcon);
    Vue.use(VeLoading);

    const versionsTableId = {
        VERSION1: 'VersionsTable1',
        VERSION2: 'VersionsTable2',
    }

    const queryInterval = 1000;

    String.prototype.capitalize = function() {
        return this.charAt(0).toUpperCase() + this.slice(1);
    }

    export default {
        name: "OrgVersions",
        data() {
            return {
                rowStyleOption: {
                  stripe: true
                },
                recordType: 'version',
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
                services: [],
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
            columns() {
                let columns = [
                    {
                        field: "",
                        key: "idx",
                        title: "",
                        width: 50,
                        align: "center",
                        fixed: "left",
                        renderBodyCell: ({ row, column, rowIndex }, h) => {
                          return ++rowIndex;
                        },
                    }
                ];

                if (this.currentTableId === versionsTableId.VERSION2) {
                    const self = this;
                    const orgColumn = {
                        field: "org",
                        key: "org",
                        title: "Org",
                        align: "left",
                        fixed: "left",
                        renderBodyCell: ({ row, column, rowIndex }, h) => {
                          const org = row[column.field];
                          return (
                              self.getOrgLabel(org)
                          );
                        },
                    };
                    const serviceNames = this.services.map(s => ({
                        key: s.key,
                        field: s.key,
                        title: s.name.capitalize(),
                        align: "right",
                    }))

                    columns = columns.concat([orgColumn]).concat(serviceNames);
                } else {
                    const serviceColumn = {
                        key: "service_name",
                        field: "service_name",
                        title: "Service",
                        align: "left",
                        fixed: "left",
                    };

                    const orgColumns = this.recordData.map(rd => {
                        const self = this;
                        return {
                            field: `org_${rd.org.id}_service`,
                            key: `org_${rd.org.id}_service`,
                            title: `Org (${rd.org.code}) Service`,
                            // _style: "min-width:50px;",
                            align: "right",
                            renderHeaderCell: ({ column }, h) => {
                              return (
                                  self.getOrgLabel(rd.org)
                              );
                            },
                            renderBodyCell: ({ row, column, rowIndex }, h) => {
                              const orgService = row[column.field];
                              return (
                                  <span>
                                      {orgService.version}
                                  </span>
                              );
                            },
                        }
                    })

                    columns = columns.concat([serviceColumn]).concat(orgColumns);
                }

                return columns
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
        },
        methods: {
            initServiceMap() {
                const serviceMap = {};

                for (let service of this.services) {
                  serviceMap[service.key] = {};
                }

                return serviceMap
            },
            getOrgLabel(org) {
                return (
                  <span>
                      <CBadge class="org-label" color="success">{org.code}</CBadge>
                      <br/>
                      {org.name}
                  </span>
              );
            },
            getServices(onSuccess, onError) {
                const url = "/api/services";
                return this.$http.get(url).then(onSuccess).catch(onError);
            },
            init() {
                let self = this;

                this.getServices().then(
                    function (response) {
                        self.services = response.data.services || [];
                        self.getRecordData().then(function (response) {
                            self.currentRecord = response.data.record;
                            if (self.currentRecord.status === self.recordStatus.PROCESSING) {
                                self.intervalRecordCheck = setInterval(self.getSyncRecordStatus, queryInterval);
                            }
                            self.recordData = response.data.record_data_rows || [];
                            self.ui.contentLoadingComplete = true;
                        }).catch()
                    }
                ).catch(function () {
                    self.$toast.error('Some errors are occurred!');
                })
            },
            getRecords() {
                const recordType = 'version';
                const url = `/api/parser/${recordType}/records`;
                return this.$http.get(url)
            },
            getRecordData() {
                const url = `/api/parser/versions-parser/records/${this.recordId}/record-data`;
                return this.$http.get(url)
            },
            getSyncRecordStatus() {
                let self = this;

                const url = `/api/parser/versions-parser/records/${this.recordId}/record-data`;
                this.$http.get(url).then(function (response) {
                    self.currentRecord = response.data.record;
                    self.recordData = response.data.record_data_rows || [];
                    if (self.intervalRecordCheck !== null && self.currentRecord.status === self.recordStatus.FINISHED) {
                        clearInterval(self.intervalRecordCheck)
                    }
                }).catch(function () {
                    self.$toast.error('Some errors are occurred!');
                })
            },
            transpose () {
                let self = this;

                this.ui.contentLoadingComplete = false;
                this.currentTableId = this.currentTableId === this.versionsTableId.VERSION2 ? this.versionsTableId.VERSION1 : this.versionsTableId.VERSION2;
                setTimeout(function () {
                   self.ui.contentLoadingComplete = true;
                }, 100);
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
                return this.$http.get(`/api/parser/versions-parser/records/${this.recordId}/excel`, {
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
                ).catch(() => {
                    self.$toast.error('Some errors are occurred!');
                });
            },
            clearIntervalCheck() {
                if (this.intervalRecordCheck) {
                    clearInterval(this.intervalRecordCheck);
                }
            }
        },
        mounted: function mounted() {
            this.init();
        },
        destroyed() {
            this.clearIntervalCheck();
        }
    }
</script>

<style scoped>
    .version-button {
        margin-left: 10px;
    }

    .org-label {
        padding: 2px;
    }
</style>