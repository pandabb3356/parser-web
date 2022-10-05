<template>
    <CCard>
        <CCardHeader>
            <span v-if="orgId">Edit the Org</span>
            <span v-else>Add the New Org</span>
        </CCardHeader>
        <CCardBody>
            <CForm v-if="ui.contentLoadingComplete">
                <CInput
                        v-model="org.name"
                        label="Name"
                        placeholder="Enter org name"
                        horizontal
                        :invalid-feedback="errors.org_name"
                        :is-valid="isValid('org_name')"
                />
                <CInput
                        v-model="org.code"
                        label="Code"
                        placeholder="Enter org code"
                        horizontal
                        :invalid-feedback="errors.org_code"
                        :is-valid="isValid('org_code')"
                />
                <CSelect
                        :value.sync="org.protocol"
                        label="Protocol"
                        :options="['http', 'https']"
                        horizontal
                        :invalid-feedback="errors.org_protocol"
                        :is-valid="isValid('org_protocol')"
                />
                <CInput
                        v-model="org.domain"
                        label="Domain"
                        placeholder="Enter org domain"
                        horizontal
                        :invalid-feedback="errors.org_domain"
                        :is-valid="isValid('org_domain')"
                />
                <CInput
                        v-model="org.tcDefaultOrgId"
                        label="TC Default Org Id"
                        placeholder="Enter tc default org id"
                        horizontal
                        :invalid-feedback="errors.tc_default_org_id"
                        :is-valid="isValid('tc_default_org_id')"
                />
                <CRow form class="form-group">
                    <CCol sm="3">
                        Is Public Cloud
                    </CCol>
                    <CInputRadioGroup
                            :checked.sync="org.isPublicCloud"
                            class="col-sm-9"
                            :options="[{value: 'true', label: 'Yes'}, {value: 'false', label: 'No'}]"
                            :inline="true"
                    />
                </CRow>
            </CForm>
        </CCardBody>
        <CCardFooter>
            <CButton type="submit" size="sm" color="primary" @click="submit">
                <CIcon name="cil-check-circle"/> Submit
            </CButton>
            &nbsp;
            <CButton type="reset" size="sm" color="danger" @click="cancel">
                <CIcon name="cil-ban"/> Cancel
            </CButton>
          </CCardFooter>
    </CCard>
</template>

<script>
    export default {
        name: "OrgDetail",
        data() {
            return {
                org: {
                    name: "",
                    code: "",
                    protocol: "http",
                    domain: "",
                    isPublicCloud: "false",
                    tcDefaultOrgId: 1
                },
                ui: {
                    contentLoadingComplete: false
                },
                errors: {}
            }
        },
        computed: {
          orgId() {
              return this.$route.params.id
          }
        },
        methods: {
            getOrg(orgId, onSuccess, onError) {
                const url = `/api/orgs/${orgId}`;

                return this.$http.get(url).then(onSuccess).catch(onError)
            },
            init() {
                const self = this;

                if (this.orgId) {
                    const onSuccess = (response) => {
                        const org = response.data.org;
                        self.$set(this.org, "code", org.code);
                        self.$set(this.org, "name", org.name);
                        self.$set(this.org, "protocol", org.protocol);
                        self.$set(this.org, "domain", org.domain);
                        self.$set(this.org, "isPublicCloud", String(org.public_cloud));
                        self.$set(this.org, "tcDefaultOrgId", org.tc_default_org_id);

                        self.ui.contentLoadingComplete = true;
                    }
                    this.getOrg(this.orgId, onSuccess, () => {})
                } else {
                    this.ui.contentLoadingComplete = true;
                }
            },
            isValid (errorKey) {
                const hasError = Boolean(this.errors && this.errors[errorKey]);
                return hasError ? false : null;
            },
            clearError (errorKey) {
                // this.errors[errorKey] should be an array
                if (this.errors && this.errors[errorKey]) {
                    delete this.errors[errorKey]
                }
            },
            submit () {
                let self = this;

                const data = {
                    org_id: this.orgId,
                    org_name: this.org.name,
                    org_code: this.org.code,
                    org_protocol: this.org.protocol,
                    org_domain: this.org.domain,
                    is_public_cloud: this.org.isPublicCloud === 'true',
                    tc_default_org_id: this.org.tcDefaultOrgId,
                };

                const url = this.orgId ? `/api/orgs/${this.orgId}` : "/api/orgs/add-org";

                let promise =  this.orgId ? this.$http.put(url, data) : this.$http.post(url, data)

                promise.then(
                    (response) => {
                        self.$toast.success(`Success!`);
                        return this.$router.push({"path": "/org/list"})
                    }
                ).catch(
                    (error) => {
                        self.$toast.error(`Some errors are occurred!`);
                        self.errors = error.response.data.errors || null;
                    }
                );
            },
            cancel() {
                return this.$router.push({"path": "/org/list"})
            }
        },
        mounted() {
            this.init();
        }
    }
</script>

<style scoped>

</style>