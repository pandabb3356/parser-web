<template>
    <ParserRecords :record-type="recordType"></ParserRecords>
</template>

<script>
import ParserRecords from "./ParserRecords";

export default {
    name: "VersionRecords",
    components: {ParserRecords},
    comments: {
        ParserRecords
    },
    data() {
      return {
          recordType: "version",
      }
    },
    methods: {

    }
}
</script>
