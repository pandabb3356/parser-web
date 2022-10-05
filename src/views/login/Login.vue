<template>
  <div class="c-app flex-row align-items-center">
    <CContainer>
      <CRow class="justify-content-center">
        <CCol md="8">
          <CCardGroup>
            <CCard class="p-4">
              <CCardBody>
                <CForm>
                  <h1>Login</h1>
                  <p class="text-muted">Sign In to your account</p>
                  <CInput
                    placeholder="Email"
                    autocomplete="Email"
                    v-model="userData.email"
                  >
                    <template #prepend-content><CIcon name="cil-user"/></template>
                  </CInput>
                  <CInput
                    placeholder="Password"
                    type="password"
                    autocomplete="curent-password"
                    v-model="userData.password"
                  >
                    <template #prepend-content><CIcon name="cil-lock-locked"/></template>
                  </CInput>
                  <CRow>
                    <CCol col="6" class="text-left">
                      <CButton color="primary" class="px-4" @click="login">Login</CButton>
                    </CCol>
                  </CRow>
                  <br />
                  <CRow>
                    <CCol col="6" class="text-left">
                      or
                    </CCol>
                  </CRow>
                  <br />
                  <CRow>
                    <CCol col="6" class="text-left">
                      <CButton color="warning" @click="goToMicrosoftLogin">
                        <CIcon name="cib-microsoft"/>
                        Microsoft Login
                      </CButton>
                    </CCol>
                  </CRow>
                </CForm>
              </CCardBody>
            </CCard>
            <CCard
              color="primary"
              text-color="white"
              class="text-center py-5 d-md-down-none"
              body-wrapper
            >
              <CCardBody>
                <h2>Hey</h2>
              </CCardBody>
            </CCard>
          </CCardGroup>
        </CCol>
      </CRow>
    </CContainer>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      userData: {
        email: '',
        password: ''
      },
      response: null,
      line: {
        linkToken: ""
      }
    }
  },
  methods: {
    getExpiredTime() {
      const now = new Date();
        const time = now.getTime();
        const expireTime = time + 1000 * 3600 * 24;

        now.setTime(expireTime);
        return now.getTime()
    },
    login() {
      const self = this;

      const data = {
        email: this.userData.email,
        password: this.userData.password,
      };

      const url = self.urlWithLinkToken("/api/login");

      this.$http.post(url, data)
        .then((response) => {
          self.$toast.success("Login Success!");

          const user = response.data.user;

          const userData = {
            id: user.id,
            name: user.name,
            email: user.email,
            expiredAt: this.getExpiredTime(),
          };

          window.localStorage.setItem('user', JSON.stringify(userData));

          self.$store.commit('global/setUser', userData);
          setTimeout(() => {
            self.$router.push({path: "/dashboard"});
          }, 200)
        }).catch((error) => {
          self.$toast.error("Login Failed!");
      })
    },
    loginCheck() {
      const self = this;

      this.$http.get("/api/login-check")
        .then((response) => {
          const user = response.data.user;

          if (user) {

            const userData = {
              id: user.id,
              name: user.name,
              email: user.email,
              expiredAt: this.getExpiredTime(),
            };

            window.localStorage.setItem('user', JSON.stringify(userData));

            self.$store.commit('global/setUser', userData);
            self.$router.push({path: "/dashboard"});
          }
        }).catch(() => {
          self.$store.commit('global/cleanUser');
      })
    },
    urlWithLinkToken(url) {
      if (this.line.linkToken) {
        return `${url}?lineLinkToken=${this.line.linkToken}`
      }
      return url
    },
    goToMicrosoftLogin() {
      const self = this;

      this.$http.get(this.urlWithLinkToken("/api/microsoft/auth")).then((response) => {
        self.response = response;
        window.location.href = response.data.auth_uri;
      })
    },
  },
  mounted() {
    this.loginCheck();
    this.line.linkToken = this.$route.query.lineLinkToken;
    this.$router.replace({query: null});

  },
}
</script>