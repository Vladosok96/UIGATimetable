$.ajax({
  url: '/get_simulators_list',
  method: 'get',
  dataType: 'json',
  data: {},
  success: function(data) {
    let simulators_body = document.getElementById("simulators-body");

    for (let i = 0; i < Object.keys(data).length; i++) {
      let simulator = data[Object.keys(data)[i]];
      let simulator_row = document.createElement("tr");
      let simulator_name = document.createElement("th");
      let simulator_caption = document.createElement("th");
      let simulator_auditory = document.createElement("th");
      let simulator_link = document.createElement("th");

      simulator_name.textContent = simulator.name;
      simulator_caption.textContent = simulator.caption;
      simulator_auditory.textContent = simulator.auditory + ' каб.';

      let simulator_a = document.createElement("a");
      simulator_a.textContent = 'Расписание полетов'
      simulator_a.setAttribute('id', 'simulator-link');
      simulator_a.setAttribute('href', '/unauthorized_timetable/' + simulator.id);

      simulator_link.appendChild(simulator_a);
      simulator_row.appendChild(simulator_name);
      simulator_row.appendChild(simulator_caption);
      simulator_row.appendChild(simulator_auditory);
      simulator_row.appendChild(simulator_link);
      simulators_body.appendChild(simulator_row);
    }
  }
});