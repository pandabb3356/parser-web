<template>
    <ParserRecords :record-type="recordType"></ParserRecords>
</template>

<script>
import ParserRecords from "./ParserRecords";

export default {
    name: "ToggleRecords",
    components: {ParserRecords},
    comments: {
        ParserRecords
    },
    data() {
      return {
          recordType: "toggle",
      }
    },
    methods: {

    }
}
</script>
