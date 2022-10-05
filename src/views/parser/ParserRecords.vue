<template>
    <CCard>
        <CCardBody>
            <CButton color="primary" class="version-button" @click="createNewRecord">
                <CIcon name="cil-plus" />
                &nbsp;
                <strong>New Record</strong>
            </CButton>
            <CDataTable
              :items="records"
              :fields="fields"
              :dark="true"
              table-filter
              items-per-page-select
              :items-per-page="ui.pageSize"
              hover
              sorter
              pagination
              header
              striped
            >
                <template #completeness="{item}">
                    <td>
                        {{ item.completeness | toInt }} %
                        <CProgress
                                v-if="item.status === statusType.PROCESSING"
                                :color="getStatusColor(item.status)" :value="item.completeness | toInt">
                        </CProgress>
                    </td>
                </template>
                <template #status="{item}">
                    <td>
                        <CBadge :color="getStatusColor(item.status)">{{ item.status }}</CBadge>
                    </td>
                </template>
                <template #created_at="{item}">
                    <td>
                        {{ item.created_at | datetime }}
                    </td>
                </template>
                <template #operation_area="{item}">
                    <td class="py-2">
                        <CButton size="sm" color="success" class="ml-1" @click="goToDetailPage(item.id)">
                            View
                        </CButton>
                        <CButton size="sm" color="danger" class="ml-1" @click="deleteRecord(item)">
                            Delete
                        </CButton>
                    </td>
                </template>
            </CDataTable>
        </CCardBody>
    </CCard>
</template>

<script>

const fields = [
  {
     key: "id",
     label: "id",
  },
  {
      key: 'completeness',
      label: 'Completeness',
  },
  {
      key: 'status',
      label: 'Status',
  },
  {
      key: 'created_at',
      label: 'Created At',
      _style: 'width:25%'
  },
  {
      key: 'operation_area',
      label: '',
      _style: 'width:20%',
      sorter: false,
      filter: false,
      align: "right"
  }
];

const statusType = {
  FINISHED: "finished",
  PROCESSING: "processing",
};


const queryInterval = 1000;

export default {
    name: "ParserRecords",
    props: {
      recordType: String,
    },
    data() {
      return {
          records: [],
          fields: fields,
          ui: {
              pageSize: 10,
          },
          statusType: statusType,
          statusColor: {
              finished: "success",
              processing: "warning",
              default: "primary"
          },
          intervalRecordCheck: null,
      }
    },
    methods: {
        getRecords(recordType, onSuccess, onError, ids="") {
            let url = `/api/parser/${recordType}/records`;
            this.$http.get(url, {params: {ids: ids}}).then(onSuccess).catch(onError)
        },
        getStatusColor(status) {
            return `${this.statusColor[status] || this.statusColor.default}`;
        },
        createNewRecord() {
            const self = this;

            const url = `/api/parser/${this.recordType}s-parser/record`;

            const onSuccess = () => {
                setTimeout(function () {
                    self.$toast.success("Created Success!");
                    self.init();
                }, 300)
            };

            const onError = (response) => {

            };

            this.$http.post(url, {}).then(onSuccess).catch(onError)
        },
        deleteRecord (record) {
            if (!record || !window.confirm(`Are you sure to delete this record (${record.id})`)) {
                return
            }

            const self = this;

            const url = `/api/parser/records/${record.id}`;

            this.$http.delete(url).then(function (response) {
                self.$toast.success(`Delete the record (${record.id}) successfully!`);

                setTimeout(function () {
                    window.location.reload();
                }, 300)

            }).catch(function () {
                self.$toast.error('Some errors are occurred!')
            })

        },
        getProcessingRecordIds() {
            const self = this;
            const recordIds = this.records.filter(r => r.status === self.statusType.PROCESSING).map(r => r.id);
            return recordIds.join(",")
        },
        updateRecordCompleteness(newRecords) {
            for (let newRecord of newRecords) {
                const recordIdx = this.records.findIndex(r => r.id === newRecord.id);
                if (recordIdx >= 0) {
                    this.$set(this.records[recordIdx], "status", newRecord.status);
                    this.$set(this.records[recordIdx], "completeness", newRecord.completeness);
                }
            }
        },
        clearIntervalCheck() {
            if (this.intervalRecordCheck) {
                clearInterval(this.intervalRecordCheck);
            }
        },
        getProcessingRecords() {
            const self = this;

            const onSuccess = (response) => {
                const records = response.data.records || [];
                self.updateRecordCompleteness(records);
                if (!this.getProcessingRecordIds()) {
                    self.clearIntervalCheck();
                }
            };

            const onError = () => {};

            const recordIds = this.getProcessingRecordIds();
            if (recordIds) {
                this.getRecords(this.recordType, onSuccess, onError, this.getProcessingRecordIds());
            }
        },
        goToDetailPage(recordId) {
            this.$router.push({
                path: `${this.recordType}/${recordId}`,
                addToHistory: false
            });
        },
        init() {
            const self = this;

            const onSuccess = (response) => {
                self.records = response.data.records;

                if (this.getProcessingRecordIds()) {
                    self.intervalRecordCheck = setInterval(self.getProcessingRecords, queryInterval);
                }
            };

            const onError = () => {};

            this.clearIntervalCheck()
            this.getRecords(this.recordType, onSuccess, onError);
        },
        destroyed() {
            this.clearIntervalCheck();
        }
    },
    mounted() {
        this.init();
    }
}
</script>
