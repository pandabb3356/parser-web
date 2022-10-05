<template>
  <CDropdown
    inNav
    class="c-header-nav-items"
    placement="bottom-end"
    add-menu-classes="pt-0"
  >
    <template #toggler>
      <CHeaderNavLink>
        <CIcon name="cil-basket"/>
      </CHeaderNavLink>
    </template>
    <CDropdownItem @click="logout">
      <a>
        <CIcon name="cil-account-logout"/> Logout
      </a>
    </CDropdownItem>
  </CDropdown>
</template>

<script>
export default {
  name: 'TheHeaderDropdownAccnt',
  data () {
    return { 
      itemsCount: 42
    }
  },
  methods: {
    logout() {
      this.$http.post("/api/logout", {}).then(() => {
        this.$store.commit("global/cleanUser");
        this.$router.push({ path: "/login" })
      });
    }
  }
}
</script>

<style scoped>
  .c-icon {
    margin-right: 0.3rem;
  }
</style>