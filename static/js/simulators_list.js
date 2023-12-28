$.ajax({
  url: '/get_simulators_list',
  method: 'get',
  dataType: 'json',
  data: {},
  success: function(data) {
    let simulators_ulist = document.getElementById("simulators-ulist");

    for (let i = 0; i < Object.keys(data).length; i++) {
      let simulator = data[Object.keys(data)[i]];
      let simulator_row = document.createElement("ul");
      let simulator_a = document.createElement("a");

      simulator_a.innerHTML = simulator.name;
      simulator_a.setAttribute('id', simulator.english_name);
      simulator_a.setAttribute('db_id', simulator.id);
      simulator_a.setAttribute('href', '/register_train/' + simulator.id);

      simulator_row.appendChild(simulator_a);
      simulators_ulist.appendChild(simulator_row);
    }
  }
});