<template>
    <CCard>
        <CCardBody>
            <CButton color="primary" @click="goToAddOrg()">
                <CIcon name="cil-plus"/>
                New Org
            </CButton>
            <CDataTable
                    :id="'orgs-list'"
                    :items="orgs"
                    :fields="fields"
                    table-filter
                    items-per-page-select
                    :items-per-page="10"
                    :hover="true"
                    sorter
                    pagination
                    :dark="true"
                    :striped="true"
            >
                <template #code="{item}">
                    <td class="py-2">
                        <CBadge color="success">{{ item.code }}</CBadge>
                    </td>
                </template>
                <template #show_details="{item, index}">
                    <td class="py-2">
                        <CButton
                                color="primary"
                                variant="outline"
                                square
                                size="sm"
                                @click="toggleDetails(item, index)"
                        >
                            {{Boolean(item._toggled) ? 'Hide' : 'Show'}}
                        </CButton>
                    </td>
                </template>
                <template #details="{item}">
                    <CCollapse :show="Boolean(item._toggled)" :duration="collapseDuration">
                        <CCardBody>
                            <CMedia :aside-image-props="{ height: 133 }">
                                <h4>
                                    <strong>{{item.name}} ({{ item.code }})</strong>
                                </h4>
                                <p class="text">Protocol: {{item.protocol}}</p>
                                <p class="text">Domain: {{item.domain}}</p>
                                <CButton size="sm" color="info" class="" @click="goToOrgDetail(item)">
                                    Org Settings
                                </CButton>
                                <CButton size="sm" color="danger" class="ml-1" @click="deleteOrg(item)">
                                    Delete
                                </CButton>
                            </CMedia>
                        </CCardBody>
                    </CCollapse>
                </template>
                <template #public_cloud="{item}">
                    <td>
                        <CIcon class="text-danger" name="cil-x-circle" v-if="!item.public_cloud"/>
                        <CIcon class="text-success" name="cil-check-circle" v-else/>
                    </td>
                </template>
            </CDataTable>
        </CCardBody>
    </CCard>
</template>

<script>

    const fields = [
        'code',
        'name',
        {key: 'public_cloud', label: "Is Public Cloud"},
        {
            key: 'show_details',
            label: '',
            _style: 'width:1%',
            sorter: false,
            filter: false
        }
    ]

    export default {
        name: 'OrgList',
        data() {
            return {
                fields,
                orgs: [],
                ui: {
                    contentLoadingComplete: false
                },
                collapseDuration: 0
            }
        },
        computed: {},
        methods: {
            initOrgs() {
                let self = this;

                const url = '/api/orgs';

                this.$http.get(url).then(function (response) {
                    self.orgs = response.data.orgs;
                }).catch()
            },
            toggleDetails(item) {
                const idx = this.orgs.findIndex(org => org.id === item.id);
                if (idx > -1) {
                    this.$set(this.orgs[idx], '_toggled', !item._toggled)
                    this.collapseDuration = 300
                    this.$nextTick(() => {
                        this.collapseDuration = 0
                    })
                }
            },
            goToOrgDetail(org) {
                this.$router.push({path: `/org/${org.id}`});
            },
            goToAddOrg() {
                this.$router.push({path: "/org/add"});
            },
            deleteOrg(org) {
                const self = this;

                const orgLabel = `org (${org.name})`;

                if (!window.confirm(`Are you sure to delete this ${orgLabel}?`)) {
                    return
                }

                const url = `/api/orgs/${org.id}`;

                this.$http.delete(url).then(function () {
                    self.$toast.success(`${orgLabel} is successfully deleted!!`);
                    setTimeout(function () {
                        window.location.reload();
                    }, 100)

                }).catch(function (error) {
                    self.$toast.error(`Some errors are occurred! ${orgLabel} is failed to deleted!!`);
                })
            },
            checkedColor(value) {
                return value ? "success" : "danger";
            }
        },
        mounted() {
            this.initOrgs();
        }

    }
</script>
