<template>
  <CRow>
    <CCol sm="6" lg="3">
      <CWidgetDropdown
        color="warning"
        :header="privateOrgCount"
        text="#. of Private Orgs"
      >

      </CWidgetDropdown>
    </CCol>
    <CCol sm="6" lg="3">
      <CWidgetDropdown
        color="danger"
        :header="publicOrgCount"
        text="#. of Public Orgs"
      >
      </CWidgetDropdown>
    </CCol>
  </CRow>
</template>

<script>

export default {
  name: 'WidgetsOrgs',
  data () {
    return {
      orgs: [],
    }
  },
  computed: {
    privateOrgCount() {
      return this.orgs.filter(org => !org.public_cloud).length.toString()
    },
    publicOrgCount() {
      return this.orgs.filter(org => org.public_cloud).length.toString()
    }
  },
  methods: {
    init () {
      this.initOrgs();
    },
    initOrgs() {
      let self = this;

      const url = '/api/orgs';

      const onSuccess = (response) => {
        self.orgs = response.data.orgs || [];
      };

      this.$http.get(url).then(onSuccess).catch()
    }
  },
  mounted() {
    this.init();
  }
}
</script>
