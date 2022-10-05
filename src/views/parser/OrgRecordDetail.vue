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
            </CRow>
            <br/>
            <ve-table v-if="currentRecord" :columns="columns" :table-data="tableData"/>
        </CCardBody>
    </CCard>
</template>

<script type="text/jsx">
    import Vue from "vue";
    import "vue-easytable/libs/theme-default/index.css"; // import style

    import { VeTable, VePagination, VeIcon, VeLoading } from "vue-easytable"; // import library

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
        name: "OrgRecordDetail",
        props: {
          recordType: String,
          columns: Array,
          tableData: Array,
          initData: Function,
        },
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
        },
        methods: {
            getOrgLabel(org) {
                return (
                  <span>
                      <CBadge class="org-label" color="success">{org.code}</CBadge>
                      <br/>
                      {org.name}
                  </span>
              );
            },
            init() {
                let self = this;

                const onServicesSuccess = (response) => {

                }

                if (this.initData) {
                    this.initData().then(
                        function (response) {
                            // self.services = response.data.services || [];
                            self.getRecordData().then(function (response) {
                                self.currentRecord = response.data.record;
                                if (self.currentRecord.status === self.recordStatus.PROCESSING) {
                                    self.intervalRecordCheck = setInterval(self.getSyncRecordStatus, queryInterval);
                                }
                                self.recordData = response.data.record_data_rows || [];

                                self.$emit("onGetRecordData")
                            }).catch()
                        }
                    ).catch(() => {})
                }
            },
            getRecordData() {
                const url = `/api/parser/${this.recordType}s-parser/records/${this.recordId}/record-data`;
                return this.$http.get(url)
            },
            getSyncRecordStatus() {
                let self = this;

                const url = `/api/parser/${this.recordType}s-parser/records/${this.recordId}/record-data`;
                this.$http.get(url).then(function (response) {
                    self.currentRecord = response.data.record;
                    self.recordData = response.data.record_data_rows || [];
                    if (self.intervalRecordCheck !== null && self.currentRecord.status === self.recordStatus.FINISHED) {
                        clearInterval(self.intervalRecordCheck)
                    }
                }).catch(() => {})
            },
            transpose () {
                let self = this;

                this.ui.contentLoadingComplete = false;
                this.currentTableId = this.currentTableId === this.versionsTableId.VERSION2 ? this.versionsTableId.VERSION1 : this.versionsTableId.VERSION2;
                setTimeout(function () {
                   self.ui.contentLoadingComplete = true;
                }, 100);
            },
            deleteRecord (record) {
                if (!record || !window.confirm(`Are you sure to delete this record (${record.id})`)) {
                    return
                }

                let self = this;

                const url = `/api/parser/records/${record.id}`;

                this.$http.delete(url).then(function (response) {
                    setTimeout(function () {
                        window.location.reload();
                    }, 300)

                }).catch(() => {})

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
            getExportExcelUrl (record) {
                return `/api/parser/${this.recordType}s-parser/records/${record.id}/excel`;
            }
        },
        mounted: function mounted() {
            this.init();
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