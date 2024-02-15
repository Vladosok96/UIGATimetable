function update_schedule() {
  $.ajax({
    url: '/get_approval',
    method: 'get',
    dataType: 'json',
    data: {},
    success: function(data) {
      let schedule_body = document.getElementById('schedule-body');
      while (schedule_body.lastElementChild) {
        schedule_body.removeChild(schedule_body.lastElementChild);
      }

      for (let i = 0; i < Object.keys(data).length; i++) {
        busy = data[Object.keys(data)[i]];
        busy_row = document.createElement('tr');
        cell_day = document.createElement('td');
        cell_slot = document.createElement('td');
        cell_company_name = document.createElement('td');
        cell_simulator_name = document.createElement('td');
        cell_customer = document.createElement('td');
        cell_action = document.createElement('td');

        cell_day.textContent = busy.day;
        cell_slot.textContent = busy.start_time + '-' + busy.end_time;
        cell_company_name.textContent = busy.company_name;
        cell_simulator_name.textContent = busy.simulator_name;
        cell_customer.textContent = busy.customer_name + ' ' + busy.customer_phone;

        busy_row.appendChild(cell_day);
        busy_row.appendChild(cell_slot);
        busy_row.appendChild(cell_company_name);
        busy_row.appendChild(cell_simulator_name);
        busy_row.appendChild(cell_customer);

        action_approve = document.createElement('button');
        action_decline = document.createElement('button');

        action_approve.textContent = '+';
        action_approve.busy_id = busy.id;
        action_approve.onclick = function(block) {
          $.ajax({
            url: '/send_approve',
            method: 'get',
            dataType: 'json',
            data: {'id': block.srcElement.busy_id, 'approved': 1},
            success: function(data) {
              update_schedule();
            }
          });
        }

        action_decline.textContent = '-';
        action_decline.busy_id = busy.id;
        action_decline.onclick = function(block) {
          $.ajax({
            url: '/send_approve',
            method: 'get',
            dataType: 'json',
            data: {'id': block.srcElement.busy_id, 'approved': 0},
            success: function(data) {
              update_schedule();
            }
          });
        }

        cell_action.appendChild(action_approve);
        cell_action.appendChild(action_decline);

        busy_row.appendChild(cell_action);

        schedule_body.appendChild(busy_row);
      }
    }
  });
}

function update_users() {
  $.ajax({
    url: '/get_user_approval',
    method: 'get',
    dataType: 'json',
    data: {},
    success: function(data) {
      let users_body = document.getElementById('users-body');
      while (users_body.firstElementChild.id != 'users-form-row') {
        users_body.removeChild(users_body.firstElementChild);
      }

      for (let i = 0; i < Object.keys(data).length; i++) {
        user = data[Object.keys(data)[i]];
        user_row = document.createElement('tr');
        cell_name = document.createElement('td');
        cell_short_name = document.createElement('td');
        cell_document_id = document.createElement('td');
        cell_mail = document.createElement('td');
        cell_action = document.createElement('td');
        
        cell_name.textContent = user.name;
        cell_short_name.textContent = user.short_name;
        cell_document_id.textContent = user.document_id_hash;
        cell_mail.textContent = user.mail;

        user_row.appendChild(cell_name);
        user_row.appendChild(cell_short_name);
        user_row.appendChild(cell_document_id);
        user_row.appendChild(cell_mail);

        action_edit = document.createElement('button');
        action_delete = document.createElement('button');

        action_edit.textContent = 'Изм.';
        action_edit.setAttribute('onclick', "location.href='/edit_company/" + user.id + "'");
        action_edit.setAttribute('type', 'button');

        action_delete.textContent = '-';
        action_delete.user_id = user.id;
        action_delete.user_name = user.name;
        action_delete.onclick = function(block) {
          if (confirm("Вы точно хотите удалить компанию " + block.srcElement.user_name + "?\nЭто действие нельязя будет отменить!")) {
            $.ajax({
              url: '/send_user',
              method: 'get',
              dataType: 'json',
              data: {'user_id': block.srcElement.user_id, 'action': 'delete'},
              success: function(data) {
                update_users();
                alert(data.response);
              }
            });
          }
        }

        cell_action.appendChild(action_edit);
        cell_action.appendChild(action_delete);

        user_row.appendChild(cell_action);

        users_body.insertBefore(user_row, users_body.lastElementChild);
      }
    }
  });
}


function update_simulators() {
  $.ajax({
    url: '/get_simulators_list',
    method: 'get',
    dataType: 'json',
    data: {},
    success: function(data) {
      let simulators_body = document.getElementById('simulators-body');
      while (simulators_body.firstElementChild.id != 'simulators-form-row') {
        simulators_body.removeChild(simulators_body.firstElementChild);
      }

      for (let i = 0; i < Object.keys(data).length; i++) {
        simulator = data[Object.keys(data)[i]];
        simulator_row = document.createElement('tr');
        cell_name = document.createElement('td');
        cell_caption = document.createElement('td');
        cell_auditory = document.createElement('td');
        cell_schedule = document.createElement('td');
        cell_action = document.createElement('td');

        cell_name.textContent = simulator.name;
        cell_caption.textContent = simulator.caption;
        cell_auditory.textContent = simulator.auditory;

        if (simulator.floating == 1) {
          cell_schedule.textContent = 'Плавающий';
        }
        else {
          cell_schedule.textContent = 'Постоянный';
        }

        simulator_row.appendChild(cell_name);
        simulator_row.appendChild(cell_caption);
        simulator_row.appendChild(cell_auditory);
        simulator_row.appendChild(cell_schedule);

        action_delete = document.createElement('button');

        action_delete.textContent = '-';
        action_delete.simulator_id = simulator.id;
        action_delete.simulator_name = simulator.name;
        action_delete.onclick = function(block) {
          if (confirm("Вы точно хотите удалить тренажер " + block.srcElement.simulator_name + "?\nЭто действие нельязя будет отменить!")) {
            $.ajax({
              url: '/send_simulator',
              method: 'get',
              dataType: 'json',
              data: {'simulator_id': block.srcElement.simulator_id, 'action': 'delete'},
              success: function(data) {
                update_simulators();
                alert(data.response);
              }
            });
          }
        }

        cell_action.appendChild(action_delete);

        simulator_row.appendChild(cell_action);

        simulators_body.insertBefore(simulator_row, simulators_body.lastElementChild);
      }
    }
  });
}


update_users();
update_schedule();
update_simulators();


var users_form = document.getElementById("users-form");

users_form.addEventListener("submit", async function(e) {
  e.preventDefault();

  values = e.srcElement;
  name = values[0].value;
  short_name = values[1].value;
  document_id = values[2].value;
  mail = values[3].value;

  $.ajax({
    url: '/send_user',
    method: 'get',
    dataType: 'json',
    data: {'name': name, 'short_name': short_name, 'document_id': document_id, 'mail': mail, 'action': 'add'},
    success: function(data) {
      update_users();
      if (data.error == true) {
        alert(data.response)
      }
    }
  });
});


var simulators_form = document.getElementById("simulators-form");

simulators_form.addEventListener("submit", async function(e) {
  e.preventDefault();

  values = e.srcElement;
  name = values[0].value;
  caption = values[1].value;
  auditory = values[2].value;
  schedule = values[3].value;

  $.ajax({
    url: '/send_simulator',
    method: 'get',
    dataType: 'json',
    data: {'name': name, 'caption': caption, 'auditory': auditory, 'schedule': schedule, 'action': 'add'},
    success: function(data) {
      update_simulators();
      if (data.error == true) {
        alert(data.response)
      }
    }
  });
});
