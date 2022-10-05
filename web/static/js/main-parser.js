if ($('#content-wrapper.versions-parser-controller').length > 0) {
    const queryInterval = 1000;

    new Vue({
        delimiters: ['[[', ']]'],
        el: '.versions-parser-controller',
        data: {
            records: [],
            currentRecord: null,
            recordData: {},
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
            currentTableId: "VersionsTable1",
            versionsTableId: {
                VERSION1: 'VersionsTable1',
                VERSION2: 'VersionsTable2',
            }
        },
        methods: {
            init() {
                let self = this;

                this.getRecords().then(
                    function (response) {
                        self.records = response.body.records || [];
                        if (self.records.length > 0) {
                            self.currentRecord = this.records[0];
                            self.getRecordData().then(function (response) {
                                self.recordData = response.body.record_data_rows || [];
                                if (self.currentRecord.status === self.recordStatus.PROCESSING) {
                                    self.intervalRecordCheck = setInterval(self.getSyncRecordStatus, queryInterval);
                                }
                                self.services = response.body.services || [];
                                self.ui.contentLoadingComplete = true;

                                self.initTable();
                            }).catch()
                        } else {
                            self.ui.contentLoadingComplete = true;
                        }
                    }
                ).catch(function () {
                    window.toastr.error('Some errors are occurred!');
                })
            },
            initTable() {
                let self = this;

                if (this.currentRecord && this.currentRecord.status === this.recordStatus.FINISHED) {
                    setTimeout(function () {
                        $(`#${self.currentTableId}`).DataTable({
                            scrollX: true,
                            paging: false,
                            fixedColumns: {
                                leftColumns: 2,
                            }
                        });

                        $('[data-toggle="tooltip"]').tooltip();
                    });
                }
            },
            getRecords() {
                const url = '/api/parser/versions-parser/records';
                return this.$http.get(url)
            },
            getRecordData() {
                const url = `/api/parser/versions-parser/records/${this.currentRecord.id}/record-data`;
                return this.$http.get(url)
            },
            getSyncRecordStatus() {
                let self = this;

                const url = `/api/parser/versions-parser/records/${this.currentRecord.id}/record-data`;
                this.$http.get(url).then(function (response) {
                    self.currentRecord = response.body.record;
                    self.recordData = response.body.record_data_rows || [];
                    if (self.intervalRecordCheck !== null && self.currentRecord.status === self.recordStatus.FINISHED) {
                        clearInterval(self.intervalRecordCheck)
                    }

                    self.initTable();
                }).catch(function () {
                    window.toastr.error('Some errors are occurred!');
                })
            },
            createNewRecord() {
                let self = this;

                const url = '/api/parser/versions-parser/record';

                this.$http.post(url, {}).then(function () {
                    window.toastr.success('Create new record successfully!');
                    setTimeout(function () {
                        window.location.reload()
                    }, 300)

                }).catch(function (repsonse) {
                    var message = repsonse.body.message ? repsonse.body.message : 'Error!';
                    window.toastr.error(message)
                })
            },
            changeRecord (record) {
                if (this.intervalRecordCheck !== null) {
                    clearInterval(self.intervalRecordCheck)
                }
                this.ui.contentLoadingComplete = false;
                this.currentRecord = record;
                this.getRecordData().then(function (response) {
                    this.recordData = response.body.record_data_rows || [];
                    if (this.currentRecord.status === this.recordStatus.PROCESSING) {
                        this.intervalRecordCheck = setInterval(this.getSyncRecordStatus, queryInterval);
                    }
                    this.services = response.body.services || [];
                    this.ui.contentLoadingComplete = true;

                    this.initTable();
                }).catch()
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
                    window.toastr.success(`Delete the record (${record.id}) successfully!`);

                    setTimeout(function () {
                        window.location.reload();
                    }, 300)

                }).catch(function () {
                    window.toastr.error('Some errors are occurred!')
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
            getExportExcelUrl (record) {
                return `/api/parser/versions-parser/records/${record.id}/excel`;
            }
        },
        mounted: function mounted() {
            this.init();
        }
    });
}

if ($('#content-wrapper.toggles-parser-controller').length > 0) {
    const queryInterval = 1000;

    new Vue({
        delimiters: ['[[', ']]'],
        el: '.toggles-parser-controller',
        data: {
            records: [],
            currentRecord: null,
            recordData: {},
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
            currentTableId: "VersionsTable1",
            versionsTableId: {
                VERSION1: 'VersionsTable1',
                VERSION2: 'VersionsTable2',
            }
        },
        methods: {
            init() {
                let self = this;

                this.getRecords().then(
                    function (response) {
                        self.records = response.body.records || [];
                        if (self.records.length > 0) {
                            self.currentRecord = this.records[0];
                            self.getRecordData().then(function (response) {
                                self.recordData = response.body.record_data_rows || [];
                                if (self.currentRecord.status === self.recordStatus.PROCESSING) {
                                    self.intervalRecordCheck = setInterval(self.getSyncRecordStatus, queryInterval);
                                }
                                self.toggles = response.body.toggles || [];
                                self.ui.contentLoadingComplete = true;

                                self.initTable();
                            }).catch()
                        } else {
                            self.ui.contentLoadingComplete = true;
                        }
                    }
                ).catch(function () {
                    window.toastr.error('Some errors are occurred!');
                })
            },
            initTable () {
                let self = this;

                var leftColumns = 2;
                if (this.currentTableId === this.versionsTableId.VERSION1) {
                    leftColumns = 3;
                }


                if (this.currentRecord && this.currentRecord.status === this.recordStatus.FINISHED) {
                    setTimeout(function () {
                        $(`#${self.currentTableId}`).DataTable({
                            scrollX: true,
                            paging: false,
                            fixedColumns: {
                                leftColumns: leftColumns,
                            }
                        });

                        $('[data-toggle="tooltip"]').tooltip();
                    });
                }
            },
            getRecords() {
                const url = '/api/parser/toggles-parser/records';
                return this.$http.get(url)
            },
            getRecordData() {
                const url = `/api/parser/toggles-parser/records/${this.currentRecord.id}/record-data`;
                return this.$http.get(url)
            },
            getSyncRecordStatus() {
                let self = this;

                const url = `/api/parser/toggles-parser/records/${this.currentRecord.id}/record-data`;
                this.$http.get(url).then(function (response) {
                    self.currentRecord = response.body.record;
                    self.recordData = response.body.record_data_rows || [];
                    if (self.intervalRecordCheck !== null && self.currentRecord.status === self.recordStatus.FINISHED) {
                        clearInterval(self.intervalRecordCheck)
                    }

                    self.initTable();
                }).catch(function () {
                    window.toastr.error('Some errors are occurred!');
                })
            },
            createNewRecord() {
                let self = this;

                const url = '/api/parser/toggles-parser/record';

                this.$http.post(url, {}).then(function () {
                    window.toastr.success('Create new record successfully!');
                    setTimeout(function () {
                        window.location.reload()
                    }, 300)

                }).catch(function (repsonse) {
                    var message = repsonse.body.message ? repsonse.body.message : 'Error!';
                    window.toastr.error(message)
                })
            },
            changeRecord (record) {
                if (this.intervalRecordCheck !== null) {
                    clearInterval(self.intervalRecordCheck)
                }
                this.ui.contentLoadingComplete = false;
                this.currentRecord = record;
                this.getRecordData().then(function (response) {
                    this.recordData = response.body.record_data_rows || [];
                    if (this.currentRecord.status === this.recordStatus.PROCESSING) {
                        this.intervalRecordCheck = setInterval(this.getSyncRecordStatus, queryInterval);
                    }
                    this.toggles = response.body.toggles || [];
                    this.ui.contentLoadingComplete = true;

                    this.initTable();
                }).catch()
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
                    window.toastr.success(`Delete the record (${record.id}) successfully!`);

                    setTimeout(function () {
                        window.location.reload();
                    }, 300)

                }).catch(function () {
                    window.toastr.error('Some errors are occurred!')
                })

            },
            hasErrorRecord (recordData) {
                return Boolean(recordData && recordData.data && recordData.data["toggles-error"])
            },
            getErrorRecord (recordData) {
                return String(recordData && recordData.data && String(recordData.data["toggles-error"])).substring(0, 20)
            },
            getErrorRecordId (recordData) {
                return `org-${recordData.org_id}-toggles-error`
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
            getExportExcelUrl (record) {
                return `/api/parser/toggles-parser/records/${record.id}/excel`;
            }
        },
        mounted: function mounted() {
            this.init();
        }
    });
}
