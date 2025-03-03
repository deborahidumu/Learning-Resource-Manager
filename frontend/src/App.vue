<script lang="ts">
  import axios from 'axios';

  axios.get('http://localhost:8000/')
  .then(function (response) {
    // handle success
    console.log(response);
  })
  .catch(function (error) {
    // handle error
    console.log(error);
  });

</script>

<template>
  <div id="app">
    <h1>Hello world</h1>
  </div>
</template>