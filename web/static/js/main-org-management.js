if ($('#content-wrapper.add-org-controller').length > 0) {
    new Vue({
        delimiters: ['[[', ']]'],
        el: '.add-org-controller',
        data: {
            org: {
                name: "",
                code: "",
                protocol: "",
                domain: "",
                isPublicCloud: false,
            },
            errors: null
        },
        methods: {
            submit () {
                let self = this;

                const url = "/api/orgs/add-org";

                const data = {
                    org_name: this.org.name,
                    org_code: this.org.code,
                    org_protocol: this.org.protocol,
                    org_domain: this.org.domain,
                    is_public_cloud: this.org.isPublicCloud,
                    tc_default_org_id: this.org.tcDefaultOrgId,
                };

                this.$http.post(url, data).then(
                    function (response) {
                        window.toastr.success('Success !');
                        setTimeout(function () {
                            window.location.href = '/sbadmin2/dashboard/orgs/org-management/existed-orgs';
                        }, 500);

                    }
                ).catch(
                    function (response) {
                        self.errors = response.body.errors || null;

                        window.toastr.error('Failed !');
                    }
                );
            },
            hasError (errorKey) {
                return Boolean(this.errors && this.errors[errorKey])
            },
            clearError (errorKey) {
                console.log(errorKey);
                // this.errors[errorKey] should be an array
                if (this.errors && this.errors[errorKey]) {
                    delete this.errors[errorKey]
                }
            }
        },
        watch: {
            "org.name": function () {
                this.clearError('org_name');
            },
            "org.code": function () {
                this.clearError('org_code');
            },
            "org.protocol": function () {
                this.clearError('org_protocol');
            },
            "org.domain": function () {
                this.clearError('org_domain');
            },
            "org.isPublicCloud": function () {
                this.clearError('is_public_cloud');
            },
            "org.tcDefaultOrgId": function () {
                this.clearError('tc_default_org_id');
            }
        }
    });
}

if ($('#content-wrapper.existed-orgs-controller').length > 0) {
    new Vue({
        delimiters: ['[[', ']]'],
        el: '.existed-orgs-controller',
        data: {
            ui: {
                contentLoadingComplete: false
            },
            orgs: []
        },
        methods: {
            init () {
                this.initOrgs()
            },
            deleteOrg (org) {
                if (!window.confirm(`Are you sure to delete this org (${org.name})?`)) {
                    return
                }

                const url = `/api/orgs/${org.id}`;

                this.$http.delete(url).then(function () {
                    window.toastr.success(`Delete the org (${org.name}) successfully!`)

                    setTimeout(function () {
                        window.location.reload();
                    }, 400)

                }).catch(function (response) {
                    window.toastr.error('Some errors are occurred!');
                })
            },
            initOrgsTable () {
                setTimeout(function () {
                    $('#existed-orgs-dataTable').DataTable();
                }, 200)
            },
            initOrgs () {
                let self = this;

                const url = '/api/orgs';

                this.$http.get(url).then(function (response) {
                    self.orgs = response.body.orgs;
                    self.ui.contentLoadingComplete = true;
                    self.initOrgsTable();
                }).catch()
            }
        },
        mounted: function mounted () {
            this.init();
        }
    });
}
