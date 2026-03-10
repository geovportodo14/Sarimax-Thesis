const axios = require('axios');
async function test() {
  const p = await axios.post('http://127.0.0.1:8000/predict', { appliance: 'aircon', history: [250], horizon: 4 });
  console.log(p.data);
}
test();
